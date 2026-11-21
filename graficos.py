from PySide6.QtWidgets import QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


def calcular_promedio(serie, ventana):
    promedios = []
    for i in range(len(serie)):
        inicio = max(0, i - ventana + 1)
        tramo = serie[inicio : i + 1]
        promedios.append(sum(tramo) / len(tramo))
    return promedios


def mostrar_figura(contenedor, figura):
    layout = contenedor.layout()
    if layout is None:
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
    else:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    canvas = FigureCanvas(figura)
    layout.addWidget(canvas)
    canvas.draw()


def grafico_margen(contenedor, datos, umbral_rssi):
    estaciones = sorted(datos.keys())
    margenes = []
    for estacion in estaciones:
        valores = datos[estacion]["rssi_dbm"]
        promedio = sum(valores) / len(valores)
        margenes.append(promedio - umbral_rssi)

    figura = Figure()
    ax = figura.add_subplot(111)
    ax.bar(estaciones, margenes, label="Margen")
    ax.axhline(0, linestyle="--", color="black", linewidth=1, label="Umbral")
    ax.set_ylabel("dB")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.legend(loc="lower left", ncol=2, frameon=False)
    figura.tight_layout()

    mostrar_figura(contenedor, figura)


def grafico_evolucion(contenedor, datos_estacion, umbral_rssi, umbral_temp, ventana):
    rssi = datos_estacion["rssi_dbm"]
    temperatura = datos_estacion["temperatura_c"]
    prom = calcular_promedio(rssi, ventana)
    muestras = list(range(len(rssi)))

    figura = Figure()
    ax1, ax2 = figura.subplots(2, 1, sharex=True)

    (linea_rssi,) = ax1.plot(muestras, rssi, linewidth=1, alpha=0.6, label="RSSI")
    (linea_prom,) = ax1.plot(muestras, prom, linewidth=2, label="Promedio")
    linea_umbral = ax1.axhline(
        umbral_rssi, linestyle="--", color="black", linewidth=1, label="Umbral"
    )
    ax1.set_ylabel("RSSI (dBm)")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)

    (linea_temp,) = ax2.plot(muestras, temperatura, linewidth=1.2, label="Temperatura")
    ax2.axhline(umbral_temp, linestyle="--", color="black", linewidth=1)
    ax2.set_ylabel("Temp (°C)")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    figura.legend(
        handles=[linea_rssi, linea_prom, linea_umbral, linea_temp],
        loc="lower center",
        ncol=4,
        frameon=False,
    )

    figura.tight_layout(rect=[0, 0.08, 1, 1])

    mostrar_figura(contenedor, figura)
