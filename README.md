## Entregable 1 y 2
Proyecto de extracción desde API yahoo a una base de datos en Amazon Redshift-

Para correr este proyecto es necesario tener las siguientes librerias instaladas:
yfinance (api de yahoo)
redshift_connector (connector a redshift)
pandas (manejo del dataframe para control de duplicidad y calculo de métricas)

Los datos de conexión se encuentran variabilizados y se ingresan desde el .py "Parametros_conexión"

----

## Entregable 3 y 4 - Proyecto final 

El objetivo del mismo es llevar nuestro ETL a airflow, que nos permite orquestar nuestro script y armar un scheduele para el mismo. Para implementar esto utilizamos Docker, que nos permite crear un entorno capaz de ejecutarse en cualquier lado. Removiendo variables como las instalación de librerias u otras dependencias. Al entregable 3 se le suma el envio de alertas SMTP en base a estado de ejecución de nuestro proceso o notificación de valores en nuestra data.

La extructura del DAG es la siguiente:

```
.
├── .airflowignore
├── ETL_stock_data_google_DAG.py
├── __init__.py
└── pyscripts
    ├── .env
    ├── Alert_monthvalues_stock_data_google.py
    ├── Extract_stock_data_google.py
    ├── Parametros_conexión.py
    ├── TransformationLoad_stock_data_google.py
    └── jars
        └── postgresql-42.2.27.jre7.jar
```
En donde:

* `ETL_stock_data_google_DAG` contiene el DAG que *orquesta* todo el proceso de *Extract + Transform + Load* de los datos. El mismo integra un envio de email SMTP en base al status de las tareas aqui definidas - Es importante destacar que las variables SMTP estan definidas dentro de airflow, por lo que si queremos ejecutar el envio de emails debemos procurar definir en airflow: SMTP_EMAIL_FROM, SMTP_EMAIL_TO y SMTP_PASSWORD.
* `Extract_stock_data_google.py.py` en el directorio `pyscripts` contiene código que realiza la extracción de la info desde la api - Escribe momentaneamente en la carpeta "Data", ubicada al mismo nivel para luego ser consumida y eliminada por el siguiente proceso
* `TransformationLoad_stock_data_google.py` realiza el proceso de transformación y carga de la data
* `Alert_monthvalues_stock_data_google.py` se encarga de enviar alerta en base a un threshold de valores definidos a traves de variables. Si quisieramos modificar la fecha a consultar, el campo o nuestro threshold solo debemos modificar las variables  dentro del codigo: field_to_check, value_to_check y  target_date. Al igual que nuestro DAG, consume variables de airflow.
* `Parametros_conexión.py` define las variables para acceso a la base de datos de redshift. Es necesario completar con nuestras credenciales para ejecutar el ETL de manera exitosa

## Para hacer el deploy:

Dentro del directorio donde su ubica nuestro docker-compose (nivel más alto):

```
docker compose up --build
```

"# DE_Coder_fvinciguerra" 
