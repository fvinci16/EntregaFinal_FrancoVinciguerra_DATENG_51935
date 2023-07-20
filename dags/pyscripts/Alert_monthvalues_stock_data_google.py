import logging
import redshift_connector
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from airflow.models import Variable
from Parametros_conexión import host, database, port, user, password

# Configuración del registro (logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def enviar(subject):
    try:
        # Obtener las credenciales de SMTP de Airflow
        smtp_email_from = Variable.get('SMTP_EMAIL_FROM')
        smtp_password = Variable.get('SMTP_PASSWORD')
        smtp_email_to = Variable.get('SMTP_EMAIL_TO')

        # Configurar conexión SMTP
        x = smtplib.SMTP('smtp.gmail.com', 587)
        x.starttls()
        x.login(smtp_email_from, smtp_password)

        # Crear mensaje
        subject = f'Alerta - {subject}'
        body_text = subject
        message = MIMEText(body_text, 'plain', 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')
        message['From'] = smtp_email_from
        message['To'] = smtp_email_to

        # Enviar correo
        x.sendmail(smtp_email_from, [smtp_email_to], message.as_string())
        x.quit()
        print('Exito al enviar el correo')
    except Exception as exception:
        print(exception)
        print('Fallo al enviar el correo')

def check_alert(connection, schema, table_name, field_to_check, value_to_check, target_date):
    try:
        # Leer los datos desde Redshift para la fecha especificada
        query = f"""
            SELECT
                "Date", {field_to_check}
            FROM
                {schema}.{table_name}
            WHERE
                "Date" = '{target_date}'
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        # Comprobar si el valor del campo especificado está por encima del umbral dado
        for result in results:
            date, field_value = result
            if field_value > value_to_check:
                alert_subject = f"{field_to_check} superó {value_to_check} para la fecha {date}"
                logging.warning(f"Alerta: ¡El campo {field_to_check} ({field_value}) para {date} está por encima de {value_to_check}!")
                enviar(alert_subject)

    except Exception as e:
        logging.error(f"Error: {str(e)}")

try:
    # Conectarse a Redshift
    connection = redshift_connector.connect(
        host=host,
        database=database,
        port=port,
        user=user,
        password=password
    )

    # Definir el esquema y los nombres de la tabla
    my_schema = "fvinciguerra_coderhouse"
    table_name = "stock_data"

    # Definir el campo y el valor a comprobar para las alertas
    field_to_check = "MonthVolume"
    value_to_check = 10000000

    # Definir la fecha objetivo (puedes cambiar esta variable para consultar distintas fechas)
    target_date = datetime(2023, 6, 30)  # Cambia esta fecha a la que desees consultar

    # Llamar a la función para comprobar la alerta
    check_alert(connection, my_schema, table_name, field_to_check, value_to_check, target_date)

    connection.close()

except Exception as e:
    logging.error(f"Error: {str(e)}")
