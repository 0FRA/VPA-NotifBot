from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()


def enviarAviso(correo, message, subject):
    # Configuración del mensaje
    msg = MIMEMultipart()
    msg["From"] = os.getenv("EMAIL_SENDER")
    msg["To"] = correo
    msg["Subject"] = subject

    # Agregar el cuerpo del mensaje
    msg.attach(MIMEText(message, "plain"))

    # Configuración del servidor SMTP
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()

    # Iniciar sesión en el servidor
    password = os.getenv("EMAIL_PASSWORD")
    server.login(msg["From"], password)

    # Enviar el mensaje
    server.sendmail(msg["From"], msg["To"], msg.as_string())
    server.quit()

    print("Correo enviado a %s con éxito!" % (msg["To"]))


# Ejemplo de uso:
# enviar_aviso(os.getenv("EMAIL_RECEIVER"), "Mensaje de ejemplo", "Asunto de ejemplo")
