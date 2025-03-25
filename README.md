📌 API de Envío de Mensajes con Flask y Telegram

Este proyecto permite el envío de mensajes a Telegram usando Flask, Telethon y MySQL, con un sistema de almacenamiento y gestión de números en una base de datos.

🚀 Instalación

1️⃣ Clonar el repositorio

git clone https://github.com/tu-repositorio.git
cd tu-repositorio

2️⃣ Crear un entorno virtual (Opcional pero recomendado)

python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

3️⃣ Instalar dependencias

pip install -r requirements.txt

4️⃣ Configurar la base de datos

Crea un archivo config.py en la raíz del proyecto con la configuración de la base de datos:

MYSQL_HOST = 'tu_host'
MYSQL_USER = 'tu_usuario'
MYSQL_PASSWORD = 'tu_contraseña'
MYSQL_DB = 'tu_base_de_datos'

5️⃣ Crear la base de datos y tablas

CREATE TABLE celulares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(20) UNIQUE NOT NULL,
    app_id INT NOT NULL,
    api_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE mensajes_enviados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(20) NOT NULL,
    usuario VARCHAR(20) NOT NULL,
    mensaje TEXT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

6️⃣ Ejecutar el servidor

python app.py

El servidor se ejecutará en http://localhost:5000

📡 Endpoints Disponibles

1️⃣ Guardar un número 📲

URL: /guardar_numero

Método: POST

Cuerpo:

{
  "numero": "+51987654321",
  "app_id": 123456,
  "api_hash": "tu_api_hash",
  "nombre": "Mi Número"
}

2️⃣ Listar números 📋

URL: /listar_numeros

Método: GET

Respuesta:

{
  "status": "success",
  "data": [
    {
      "id": 1,
      "numero": "+51987654321",
      "nombre": "Mi Número"
    }
  ]
}

3️⃣ Enviar mensaje ✉️

URL: /enviar_mensaje

Método: POST

Cuerpo:

{
  "id_celular": 1,
  "destinatario": "+51948061056",
  "mensaje": "Hola bro",
  "titulo": "Saludo"
}

Respuesta:

{
  "status": "success",
  "message": "Mensaje enviado a +51948061056"
}

🚀 ¡Listo! Ahora puedes usar la API para enviar mensajes a Telegram.

