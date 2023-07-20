from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import DAG, Variable
import os
import smtplib

email_success = 'SUCCESS'
email_failure = 'FAILURE'

def enviar_error():
    enviar(email_failure)

def enviar_success():
    enviar(email_success)

def enviar(subject):
    try:
        x=smtplib.SMTP('smtp.gmail.com',587)
        x.starttls()
        x.login(Variable.get('SMTP_EMAIL_FROM'),Variable.get('SMTP_PASSWORD'))
        subject=f'El dag termino en: {subject}'
        body_text=subject
        message='Subject: {}\n\n{}'.format(subject,body_text)
        x.sendmail(Variable.get('SMTP_EMAIL_FROM'),Variable.get('SMTP_EMAIL_TO'),message)
        print('Exito al enviar el mail')
    except Exception as exception:
        print(exception)
        print('Fallo al enviar el mail')

# Ruta ETL
extract_script_path = os.path.join(os.path.dirname(__file__), 'pyscripts/Extract_stock_data_google.py')
transform_load_script_path = os.path.join(os.path.dirname(__file__), 'pyscripts/TransformationLoad_stock_data_google.py')
envio_alerta_script_path =  os.path.join(os.path.dirname(__file__), 'pyscripts/Alert_monthvalues_stock_data_google.py')

default_args = {
    "owner": "fvinciguerra",
    "start_date": datetime(2023, 7, 13),
    "retries": 0,
    "retry_delay": timedelta(seconds=5),
}

with DAG(
    dag_id="ETL_stock_data_google_DAG",
    default_args=default_args,
    description="ETL de la tabla stock_data para Google (yfinance)",
    schedule_interval="@daily",
    catchup=False,
) as dag:
    extract_task = BashOperator(
        task_id="extract_data",
        bash_command=f"python {extract_script_path}",
        dag=dag,
    )

    transform_load_task = BashOperator(
        task_id="transform_load_data",
        bash_command=f"python {transform_load_script_path}",
        dag=dag,
    )

    envio_success = PythonOperator(
        task_id='dag_envio_success',
        python_callable=enviar_success,
        trigger_rule='all_success',
        dag=dag,
    )

    envio_error = PythonOperator(
        task_id='dag_envio_error',
        python_callable=enviar_error,
        trigger_rule='all_failed',
        dag=dag,
    )

    envio_alerta_valores = BashOperator(
        task_id="dag_envio_alerta",
        bash_command=f"python {envio_alerta_script_path}",
        dag=dag,
    )

    extract_task >> transform_load_task >> [envio_success, envio_error]
    envio_success >> envio_alerta_valores