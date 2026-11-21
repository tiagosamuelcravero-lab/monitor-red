import csv

def cargar_csv(ruta_archivo):
    datos = {}
    with open(ruta_archivo , mode="r", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        if not lector.fieldnames:
            raise ValueError("El archivo CSV esta vacio.")
        lector.fieldnames = [col.strip() for col in lector.fieldnames]
        col_obligatorias = ["timestamp", "estacion", "rssi_dbm", "temperatura_c"]
        for col in col_obligatorias:
            if col not in lector.fieldnames:
                raise ValueError("El archivo no tiene el formato esperado (faltan columnas obligatorias).")
        for fila in lector:
            try:
                timestamp = fila["timestamp"].strip()
                estacion = fila["estacion"].strip()
                rssi_dbm = float(fila["rssi_dbm"])
                temperatura_c = float(fila["temperatura_c"])
            except(ValueError, TypeError, AttributeError):
                raise ValueError("El archivo tiene datos invalidos o incompletos.")

            if estacion not in datos:
                datos[estacion] = {
                    "timestamp" : [],
                    "rssi_dbm" : [],
                    "temperatura_c" : []
                }
            datos[estacion]["timestamp"].append(timestamp)
            datos[estacion]["rssi_dbm"].append(rssi_dbm)
            datos[estacion]["temperatura_c"].append(temperatura_c)
    if not datos:
        raise ValueError("El archivo CSV no contiene registros.")
    return datos