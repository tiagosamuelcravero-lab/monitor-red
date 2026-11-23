def calcular_promedio_movil(valores, ventana):
    if ventana <= 0:
        raise ValueError("La ventana del promedio móvil debe ser mayor a 0.")
    promedios = []
    for i in range(len(valores)):
        inicio = max(0, i - ventana + 1)
        sublista = valores[inicio : i + 1]
        promedios.append(sum(sublista) / len(sublista))

    return promedios


def analizar_estaciones(datos, umbral_rssi, umbral_temp, ventana):
    resultados = {}
    problemas = []

    for estacion, series in datos.items():
        rssi = series["rssi_dbm"]
        temp = series["temperatura_c"]

        rssi_prom = sum(rssi) / len(rssi)
        temp_prom = sum(temp) / len(temp)
        margen_rssi = rssi_prom - umbral_rssi

        rssi_movil = calcular_promedio_movil(rssi, ventana)
        temp_movil = calcular_promedio_movil(temp, ventana)

        alertas_rssi = len([v for v in rssi if v < umbral_rssi])
        alertas_temp = len([v for v in temp if v > umbral_temp])

        if alertas_rssi > 0:
            problemas.append(
                f"{estacion}: {alertas_rssi} muestras con RSSI bajo (< {umbral_rssi} dBm)."
            )

        if alertas_temp > 0:
            problemas.append(
                f"{estacion}: {alertas_temp} muestras con temperatura alta (> {umbral_temp} °C)."
            )

        resultados[estacion] = {
            "muestras": len(rssi),
            "rssi_prom": rssi_prom,
            "rssi_min": min(rssi),
            "rssi_max": max(rssi),
            "margen_rssi": margen_rssi,
            "temp_prom": temp_prom,
            "temp_min": min(temp),
            "temp_max": max(temp),
            "rssi_movil": rssi_movil,
            "temp_movil": temp_movil,
        }

    return resultados, problemas


if __name__ == "__main__":
    from datos_csv import cargar_csv

    datos = cargar_csv("datos/telemetria.csv")
    res, probs = analizar_estaciones(datos, umbral_rssi=-80, umbral_temp=40, ventana=3)

    print("--- PROBLEMAS ---")
    for p in probs:
        print(p)

    print("\n--- RESULTADOS ---")
    for est, info in res.items():
        print(
            f"{est}: RSSI prom={info['rssi_prom']:.2f} dBm | Margen={info['margen_rssi']:.2f} dB | Temp prom={info['temp_prom']:.2f} °C"
        )
