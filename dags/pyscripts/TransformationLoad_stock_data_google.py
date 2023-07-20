import logging
import os
import redshift_connector
import pandas as pd
from Parametros_conexión import host, database, port, user, password

# Configuración del registro (logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Carpeta para la extracción
    extraction_folder = 'data'

    # Carpeta para la transformación
    transformation_folder = os.path.join(os.path.dirname(__file__), extraction_folder)

    # Cargo el csv
    file_path = os.path.join(transformation_folder, 'extracted_data.csv')
    hist = pd.read_csv(file_path)

    # Borro el archivo
    os.remove(file_path)

    # Transformación
    logging.info("Iniciando transformación de datos...")

    # Convierto Date a datetype
    hist['Date'] = pd.to_datetime(hist['Date'])

    # Ordeno el DataFrame por 'Date'
    hist = hist.sort_values('Date')

    # Remuevo duplicados si es que hay
    hist = hist.drop_duplicates(subset=['Date'], keep='last')

    # Extraigo mes - Necesario para el calculo de volumen por mes
    hist['Month'] = hist['Date'].apply(lambda x: x.month)

    # Calculo de volumen por mes
    hist['MonthVolume'] = hist.groupby('Month')['Volume'].transform('sum')

    # Seteo columna que define la fuente
    hist['Source'] = 'Google'
    logging.info("Transformación de datos completada.")

    # Carga
    logging.info("Iniciando carga de datos...")
    connection = redshift_connector.connect(
        host=host,
        database=database,
        port=port,
        user=user,
        password=password
    )

    my_schema = "fvinciguerra_coderhouse"
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {my_schema}.stock_data (
            Date DATE,
            "Open" DECIMAL,
            High DECIMAL,
            Low DECIMAL,
            Close DECIMAL,
            Volume DECIMAL,
            Dividends DECIMAL,
            Stock_Splits DECIMAL,
            MonthVolume DECIMAL(30, 2),
            Source VARCHAR(50)
        )
        SORTKEY (Date)
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)

    truncate_table_query = f"""
        TRUNCATE TABLE {my_schema}.stock_data
    """
    cursor.execute(truncate_table_query)

    insert_query = f"""
        INSERT INTO {my_schema}.stock_data
        (Date, "Open", High, Low, Close, Volume, Dividends, Stock_Splits, MonthVolume, Source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = hist[
        ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock_Splits', 'MonthVolume', 'Source']
    ].values
    with connection.cursor() as cursor:
        cursor.executemany(insert_query, values)

    connection.commit()
    connection.close()
    logging.info("Carga de datos completada.")

    # Imprimir estado
    logging.info("La inserción de 'stock_data' se completó exitosamente")

except Exception as e:
    logging.error(f"Error: {str(e)}")
