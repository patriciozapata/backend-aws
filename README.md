
Proyecto Zock Backend  ![Captura de pantalla 2024-12-06 a la(s) 7 24 45 p m](https://github.com/user-attachments/assets/06bc631e-c0b4-4c02-be60-fa69b9c4ec74)

Este proyecto es un prototipo funcional que conecta una API Gateway con una instancia EC2 utilizando AWS Lambda, S3 y otros servicios de AWS. Está diseñado para ejecutar scripts específicos en la instancia EC2, como bots de Selenium, de manera controlada y segura.

Diagrama del Flujo
plaintext
Copiar código
Cliente -> API Gateway -> Lambda -> EC2 -> Script (descargado desde S3 y ejecutado)
Cliente: Realiza una solicitud HTTP al API Gateway, proporcionando el nombre del script y parámetros adicionales en el cuerpo de la solicitud.
API Gateway: Recibe la solicitud y la pasa al servicio AWS Lambda.
Lambda:
Verifica los parámetros proporcionados.
Interactúa con Secrets Manager para recuperar la clave SSH.
Se conecta a la instancia EC2 mediante SSH.
Descarga y ejecuta el script en la instancia EC2.
EC2:
Descarga el script desde S3 si no está presente.
Ejecuta el script con los parámetros recibidos.
Devuelve el resultado o los errores de la ejecución a Lambda.
Respuesta: Lambda envía la respuesta de la ejecución del script al cliente a través del API Gateway.
Componentes del Sistema
1. API Gateway
Sirve como punto de entrada para el sistema.
Acepta solicitudes HTTP POST con los siguientes parámetros en el cuerpo:
json
Copiar código
{
  "scriptname": "nombre_del_script.py",
  "parameter": "parametro_opcional"
}
2. AWS Lambda
Orquesta la lógica de negocio y comunicación entre los servicios.
Principales responsabilidades:
Recuperar la clave SSH desde Secrets Manager.
Conectar a EC2 vía SSH usando paramiko.
Descargar el script desde S3 si no está disponible en EC2.
Ejecutar el script en EC2 con los parámetros proporcionados.
3. Instancia EC2
Ejecuta los scripts proporcionados por el cliente.
Preparada con:
Python3, pip, y bibliotecas como pandas, selenium, etc.
Google Chrome y ChromeDriver para scripts de Selenium.
4. S3
Almacena los scripts que deben ejecutarse en EC2.
Estructura esperada:
php
Copiar código
s3://<BucketName>/<ScriptFolder>/<ScriptName>
5. Secrets Manager
Almacena de manera segura la clave privada SSH para conectarse a EC2.
Requisitos Previos
Infraestructura AWS Configurada:
Desplegar la plantilla template.yml usando AWS CloudFormation o SAM CLI.
Script en S3:
Subir el script Python al bucket especificado en el parámetro BucketName.
Claves SSH en Secrets Manager:
Almacenar la clave SSH en un secreto con el formato:
json
Copiar código
{
  "my-ec2-keypair": "contenido_de_la_clave_privada"
}
Instrucciones de Uso
1. Solicitud HTTP al API Gateway
Envía una solicitud POST al endpoint del API Gateway:

bash
Copiar código
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"scriptname": "test.py", "parameter": "argumento"}' \
  https://<api-id>.execute-api.<region>.amazonaws.com/Prod/invoke
2. Ejecución del Script
Lambda verifica y envía los parámetros a EC2.
EC2 ejecuta el script y devuelve el resultado.
3. Respuesta
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
La instancia EC2 y Lambda tienen permisos mínimos necesarios para interactuar con S3 y Secrets Manager.
Clave SSH:
Almacenada de forma segura en Secrets Manager.
Usada con permisos restrictivos para conexiones SSH.
Scripts Controlados:
Solo se ejecutan scripts desde un bucket S3 confiable.
Pruebas
Escenarios Probados
Ejecución exitosa del script en EC2.
Manejo de errores:
Script no encontrado.
Dependencias no instaladas.
Parámetros faltantes.
Comando de Ejemplo
bash
Copiar código
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"scriptname": "test_2.py", "parameter": "valor"}' \
  https://<api-id>.execute-api.<region>.amazonaws.com/Prod/invoke
Mejoras Futuras
Registro de Ejecuciones:
Implementar CloudWatch Logs para el historial de ejecuciones.
Validación de Parámetros:
Validar la existencia de scripts en S3 antes de ejecutar.
Optimización de Recursos:
Apagar la instancia EC2 automáticamente tras un periodo de inactividad.
Espero que esta documentación sea útil para describir y manejar el proyecto. ¿Te gustaría agregar algo más?







Proyecto Zock Backend
Este proyecto es un prototipo funcional que conecta una API Gateway con una instancia EC2 utilizando AWS Lambda, S3 y otros servicios de AWS. Está diseñado para ejecutar scripts específicos en la instancia EC2, como bots de Selenium, de manera controlada y segura.

Diagrama del Flujo
plaintext
Copiar código
Cliente -> API Gateway -> Lambda -> EC2 -> Script (descargado desde S3 y ejecutado)
Cliente: Realiza una solicitud HTTP al API Gateway, proporcionando el nombre del script y parámetros adicionales en el cuerpo de la solicitud.
API Gateway: Recibe la solicitud y la pasa al servicio AWS Lambda.
Lambda:
Verifica los parámetros proporcionados.
Interactúa con Secrets Manager para recuperar la clave SSH.
Se conecta a la instancia EC2 mediante SSH.
Descarga y ejecuta el script en la instancia EC2.
EC2:
Descarga el script desde S3 si no está presente.
Ejecuta el script con los parámetros recibidos.
Devuelve el resultado o los errores de la ejecución a Lambda.
Respuesta: Lambda envía la respuesta de la ejecución del script al cliente a través del API Gateway.
Componentes del Sistema
1. API Gateway
Sirve como punto de entrada para el sistema.
Acepta solicitudes HTTP POST con los siguientes parámetros en el cuerpo:
json
Copiar código
{
  "scriptname": "nombre_del_script.py",
  "parameter": "parametro_opcional"
}
2. AWS Lambda
Orquesta la lógica de negocio y comunicación entre los servicios.
Principales responsabilidades:
Recuperar la clave SSH desde Secrets Manager.
Conectar a EC2 vía SSH usando paramiko.
Descargar el script desde S3 si no está disponible en EC2.
Ejecutar el script en EC2 con los parámetros proporcionados.
3. Instancia EC2
Ejecuta los scripts proporcionados por el cliente.
Preparada con:
Python3, pip, y bibliotecas como pandas, selenium, etc.
Google Chrome y ChromeDriver para scripts de Selenium.
4. S3
Almacena los scripts que deben ejecutarse en EC2.
Estructura esperada:
php
Copiar código
s3://<BucketName>/<ScriptFolder>/<ScriptName>
5. Secrets Manager
Almacena de manera segura la clave privada SSH para conectarse a EC2.
Requisitos Previos
Infraestructura AWS Configurada:
Desplegar la plantilla template.yml usando AWS CloudFormation o SAM CLI.
Script en S3:
Subir el script Python al bucket especificado en el parámetro BucketName.
Claves SSH en Secrets Manager:
Almacenar la clave SSH en un secreto con el formato:
json
Copiar código
{
  "my-ec2-keypair": "contenido_de_la_clave_privada"
}
Instrucciones de Uso
1. Solicitud HTTP al API Gateway
Envía una solicitud POST al endpoint del API Gateway:

bash
Copiar código
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"scriptname": "test.py", "parameter": "argumento"}' \
  https://<api-id>.execute-api.<region>.amazonaws.com/Prod/invoke
2. Ejecución del Script
Lambda verifica y envía los parámetros a EC2.
EC2 ejecuta el script y devuelve el resultado.
3. Respuesta
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
La instancia EC2 y Lambda tienen permisos mínimos necesarios para interactuar con S3 y Secrets Manager.
Clave SSH:
Almacenada de forma segura en Secrets Manager.
Usada con permisos restrictivos para conexiones SSH.
Scripts Controlados:
Solo se ejecutan scripts desde un bucket S3 confiable.
Pruebas
Escenarios Probados
Ejecución exitosa del script en EC2.
Manejo de errores:
Script no encontrado.
Dependencias no instaladas.
Parámetros faltantes.
Comando de Ejemplo
bash
Copiar código
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"scriptname": "test_2.py", "parameter": "valor"}' \
  https://<api-id>.execute-api.<region>.amazonaws.com/Prod/invoke
Mejoras Futuras
Registro de Ejecuciones:
Implementar CloudWatch Logs para el historial de ejecuciones.
Validación de Parámetros:
Validar la existencia de scripts en S3 antes de ejecutar.
Optimización de Recursos:
Apagar la instancia EC2 automáticamente tras un periodo de inactividad.
Espero que esta documentación sea útil para describir y manejar el proyecto. ¿Te gustaría agregar algo más?






