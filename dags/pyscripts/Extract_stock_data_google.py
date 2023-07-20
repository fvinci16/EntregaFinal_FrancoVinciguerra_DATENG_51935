import logging
import os
import pandas as pd
import yfinance as yf

# Configuración del registro (logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Extracción
    logging.info("Iniciando extracción de datos...")
    goo = yf.Ticker('GOOG')
    hist = goo.history(period="1y")
    logging.info("Extracción de datos completada.")

    # Reseteo de index - Es necesario para el cálculo de Month Volume
    hist = hist.reset_index()

    # Convierto 'Date' a Datetype para luego calcular el volumen por mes
    hist['Date'] = pd.to_datetime(hist['Date'])

    # Si la columna 'Stock_Splits' no existe, se establece en 0
    if 'Stock_Splits' not in hist.columns:
        hist['Stock_Splits'] = 0
    else:
        hist['Stock_Splits'] = hist['Stock_Splits'].fillna(0)

    # Create a folder named "data" in the same directory as the script if it doesn't exist
    folder_path = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save the extracted data to the "data" folder
    file_path = os.path.join(folder_path, 'extracted_data.csv')
    hist.to_csv(file_path, index=False)
    logging.info("Datos extraídos guardados exitosamente.")

except Exception as e:
    logging.error(f"Error: {str(e)}")

