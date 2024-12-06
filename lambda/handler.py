import boto3
import os
import paramiko
import json
import logging

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def format_pem_key(raw_key_body):
    """
    Formatea el cuerpo de una clave privada en un formato válido PEM.
    """
    formatted_body = "\n".join([raw_key_body[i:i+64] for i in range(0, len(raw_key_body), 64)])
    return f"-----BEGIN RSA PRIVATE KEY-----\n{formatted_body}\n-----END RSA PRIVATE KEY-----"

def validate_key_is_rsa(key_path):
    """
    Valida si una clave privada es de tipo RSA usando Paramiko.
    """
    try:
        paramiko.RSAKey.from_private_key_file(key_path)
        logger.info("SSH private key is valid RSA.")
    except paramiko.SSHException as key_error:
        raise ValueError(f"Invalid SSH private key: {key_error}")

def get_ssh_key_from_secrets_manager():
    """
    Recupera la clave privada desde AWS Secrets Manager, valida o corrige el formato, y la guarda temporalmente.
    """
    try:
        region = os.getenv('REGION', 'us-east-1')
        secrets_client = boto3.client('secretsmanager', region_name=region)
        secret_name = os.getenv('SECRET_NAME')
        logger.info(f"Fetching SSH key from Secrets Manager: {secret_name}")
        
        # Ruta del archivo PEM
        key_path = '/tmp/my-ec2-keypair.pem'
        
        # Verificar si el archivo ya existe
        if os.path.exists(key_path):
            logger.info(f"Key already exists at {key_path}. Ensuring permissions are correct.")
            os.chmod(key_path, 0o400)  # Asegurar permisos restrictivos
            return key_path

        # Obtener la clave desde Secrets Manager
        secret = secrets_client.get_secret_value(SecretId=secret_name)
        secret_string = secret['SecretString']
        
        # Extraer contenido de clave
        try:
            secret_data = json.loads(secret_string)
            key_content = secret_data.get("my-ec2-keypair")
            if not key_content:
                raise ValueError("The key 'my-ec2-keypair' was not found in the secret JSON.")
        except json.JSONDecodeError:
            logger.warning("Secret is not JSON. Assuming plain key content.")
            key_content = secret_string

        # Reformatear la clave si es necesario
        if "-----BEGIN RSA PRIVATE KEY-----" not in key_content or "-----END RSA PRIVATE KEY-----" not in key_content:
            key_content = format_pem_key(key_content)

        # Guardar archivo PEM con permisos seguros
        with open(key_path, 'w') as key_file:
            key_file.write(key_content)

        os.chmod(key_path, 0o400)  # Permisos restrictivos
        validate_key_is_rsa(key_path)
        logger.info(f"Key saved to {key_path} and validated.")
        return key_path
    except Exception as e:
        logger.error(f"Error retrieving SSH key from Secrets Manager: {str(e)}")
        raise


def get_instance_ip(instance_id):
    """
    Obtiene la dirección IP pública de la instancia EC2 a partir del ID de la instancia.
    """
    try:
        region = os.getenv('REGION', 'us-east-1')
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        logger.info(f"Public IP for instance {instance_id}: {instance_ip}")
        return instance_ip
    except Exception as e:
        logger.error(f"Error retrieving EC2 public IP: {str(e)}")
        raise

def execute_script_on_ec2(instance_ip, script_name, parameter):
    """
    Conecta a la instancia EC2, descarga el script si no existe y lo ejecuta.
    """
    try:
        ssh_key_path = get_ssh_key_from_secrets_manager()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=instance_ip, username='ec2-user', key_filename=ssh_key_path)

        # Verificar si el script existe y descargarlo si no está presente
        check_command = f"ls /home/ec2-user/{script_name}"
        stdin, stdout, stderr = client.exec_command(check_command)
        if stderr.read().decode().strip():
            logger.info(f"{script_name} no encontrado. Descargando desde S3...")
            download_command = f"aws s3 cp s3://{os.getenv('BUCKET_NAME')}/{os.getenv('SCRIPT_FOLDER')}/{script_name} /home/ec2-user/{script_name}"
            stdin, stdout, stderr = client.exec_command(download_command)
            download_error = stderr.read().decode().strip()
            if download_error:
                raise RuntimeError(f"Error descargando el script: {download_error}")

        # Ejecutar el script
        command = f"python3 /home/ec2-user/{script_name} {parameter}"
        stdin, stdout, stderr = client.exec_command(command)
        result = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        client.close()

        if error:
            logger.error(f"Error ejecutando el script: {error}")
            return {"statusCode": 500, "body": error}
        
        logger.info(f"Resultado del script: {result}")
        return {"statusCode": 200, "body": result}
    except Exception as e:
        logger.error(f"Error during SSH execution: {str(e)}")
        return {"statusCode": 500, "body": str(e)}


def lambda_handler(event, context):
    """
    Manejador principal de Lambda para recibir parámetros de API Gateway y ejecutar en EC2.
    """
    try:
        # Detectar si el evento contiene 'body' o ya es un JSON plano
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        # Obtener parámetros
        script_name = body.get('scriptname', 'test.py')  # Nota: 'scriptname', no 'script_name'
        script_parameter = body.get('parameter', '')

        if not script_name:
            raise ValueError("The parameter 'scriptname' is required in the request body.")

        # Variables de entorno
        EC2_INSTANCE_ID = os.getenv('EC2_INSTANCE_ID')
        if not EC2_INSTANCE_ID:
            raise ValueError("EC2_INSTANCE_ID environment variable is not set.")
        
        # Obtener la IP pública de la instancia EC2
        instance_ip = get_instance_ip(EC2_INSTANCE_ID)
        
        # Ejecutar el script en EC2 vía SSH
        result = execute_script_on_ec2(instance_ip, script_name, script_parameter)
        return result
    except Exception as e:
        logger.error(f"Error in Lambda handler: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

