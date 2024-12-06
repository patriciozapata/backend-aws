
Proyecto Zock Backend  ![Captura de pantalla 2024-12-06 a la(s) 7 24 45 p m](https://github.com/user-attachments/assets/06bc631e-c0b4-4c02-be60-fa69b9c4ec74)

Descripción del Proyecto
Este proyecto es un prototipo funcional que conecta una API Gateway con una instancia EC2 utilizando AWS Lambda, S3 y otros servicios de AWS. Está diseñado para ejecutar scripts específicos en la instancia EC2, como bots de Selenium, de manera controlada y segura.

Diagrama del Flujo

Cliente -> API Gateway -> Lambda -> EC2 -> Script (descargado desde S3 y ejecutado)

1. Cliente: Realiza una solicitud HTTP al API Gateway, proporcionando el nombre del script y parámetros adicionales en el cuerpo de la solicitud.
2. API Gateway: Recibe la solicitud y la pasa al servicio AWS Lambda.
3. Lambda:
   - Verifica los parámetros proporcionados.
   - Interactúa con Secrets Manager para recuperar la clave SSH.
   - Se conecta a la instancia EC2 mediante SSH.
   - Descarga y ejecuta el script en la instancia EC2.
4. EC2:
   - Descarga el script desde S3 si no está presente.
   - Ejecuta el script con los parámetros recibidos.
   - Devuelve el resultado o los errores de la ejecución a Lambda.
5. Respuesta: Lambda envía la respuesta de la ejecución del script al cliente a través del API Gateway.


Componentes del Sistema
1. API Gateway
Función: Punto de entrada para el sistema.
Parámetros esperados en solicitudes HTTP POST:
json
Copiar código
{
  "scriptname": "nombre_del_script.py",
  "parameter": "parametro_opcional"
}
2. AWS Lambda
Responsabilidades principales:
Recuperar la clave SSH desde Secrets Manager.
Conectarse a EC2 vía SSH utilizando paramiko.
Descargar el script desde S3 si no está disponible en EC2.
Ejecutar el script en EC2 con los parámetros proporcionados.
3. Instancia EC2
Funciones:
Ejecutar los scripts solicitados por el cliente.
Preparada con:
Python3 y dependencias (pandas, selenium, etc.).
Google Chrome y ChromeDriver para scripts de Selenium.
4. S3
Uso: Almacén de scripts que deben ejecutarse en EC2.
Estructura esperada:
php
Copiar código
s3://<BucketName>/<ScriptFolder>/<ScriptName>
5. Secrets Manager
Uso: Almacenar la clave privada SSH para conectarse a EC2 de forma segura.
Formato del secreto:
json
Copiar código
{
  "my-ec2-keypair": "contenido_de_la_clave_privada"
}
Requisitos Previos
Infraestructura AWS Configurada:

Desplegar la plantilla template.yml con AWS CloudFormation o SAM CLI.
Script en S3:

Subir los scripts Python al bucket especificado.
Claves SSH en Secrets Manager:

Configurar la clave SSH en Secrets Manager con el formato esperado.
Instrucciones de Uso
Solicitud HTTP al API Gateway:

bash
Copiar código
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"scriptname": "test.py", "parameter": "argumento"}' \
  https://<api-id>.execute-api.<region>.amazonaws.com/Prod/invoke
Ejecución del Script:

Lambda verifica y envía los parámetros a EC2.
EC2 ejecuta el script y devuelve el resultado.
Respuesta:

El cliente recibe una respuesta JSON con el resultado o un mensaje de error.
Estructura del Proyecto
plaintext
Copiar código
├── lambda/                # Código de la función Lambda
│   ├── handler.py         # Lógica principal
│   ├── requirements.txt   # Dependencias para Lambda
│   ├── __init__.py        # Archivo de inicialización
├── template.yml           # Plantilla CloudFormation para desplegar la infraestructura
├── README.md              # Documentación del proyecto
Consideraciones de Seguridad
Roles y Permisos:

Instancia EC2 y Lambda con permisos mínimos necesarios para interactuar con S3 y Secrets Manager.
Clave SSH:

Almacenada en Secrets Manager y usada con permisos restrictivos.
Ejecución Controlada:

Solo se ejecutan scripts desde un bucket S3 confiable.
Pruebas
Escenarios Probados:

Ejecución exitosa del script en EC2.
Manejo de errores:
Script no encontrado.
Dependencias no instaladas.
Parámetros faltantes.
Comando de Ejemplo:

bash
Copiar código
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"scriptname": "test_2.py", "parameter": "valor"}' \
  https://<api-id>.execute-api.<region>.amazonaws.com/Prod/invoke
Mejoras Futuras
Registro de Ejecuciones:

Implementar CloudWatch Logs para almacenar el historial de ejecuciones.
Validación de Parámetros:

Verificar la existencia de scripts en S3 antes de ejecutar.
Optimización de Recursos:

Apagar la instancia EC2 automáticamente tras un periodo de inactividad.
