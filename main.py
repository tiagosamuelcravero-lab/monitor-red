import os
import sys
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from analisis import analizar_estaciones
from datos_csv import cargar_csv
from graficos import grafico_margen, grafico_evolucion, limpiar_grafico


class MonitorRed:
    def __init__(self):
        loader = QUiLoader()
        archivo_ui = QFile("ui/ventana_principal.ui")
        archivo_ui.open(QFile.ReadOnly)
        self.ui = loader.load(archivo_ui)
        archivo_ui.close()

        self.datos = None
        self.ui.action_abrir_CSV.triggered.connect(self.abrir_csv)
        self.ui.btn_analizar.clicked.connect(self.analizar)
        self.ui.action_cerrar.triggered.connect(self.cerrar)
        self.umbral_rssi = None
        self.umbral_temp = None
        self.ventana = None
        self.ui.comboBox_estacion.currentTextChanged.connect(self.actualizar_estacion)

    def abrir_csv(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self.ui,
            "Seleccionar archivo de telemetría",
            "",
            "Archivos CSV (*.csv);;Todos los archivos (*)",
        )
        if not ruta:
            return

        try:
            self.datos = cargar_csv(ruta)
            nombre_archivo = os.path.basename(ruta)
            self.ui.espacio_archivo.setText(nombre_archivo)
            QMessageBox.information(
                self.ui,
                "Archivo cargado",
                f"Se cargaron {len(self.datos)} estaciones correctamente.",
            )
        except (ValueError, FileNotFoundError) as error:
            QMessageBox.critical(self.ui, "Error al cargar CSV", str(error))

    def analizar(self):
        if not self.datos:
            QMessageBox.warning(
                self.ui, "Atención", "Antes debes cargar un archivo CSV."
            )
            return

        try:
            umbral_rssi = float(self.ui.espacio_rssi.text())
            umbral_temp = float(self.ui.espacio_temp.text())
            ventana = int(self.ui.espacio_ventanapromedio.text())
        except ValueError:
            QMessageBox.critical(
                self.ui,
                "Parámetros inválidos",
                "Ingresá números válidos (RSSI y temperatura en decimales y ventana en enteros).",
            )
            return

        if not (-120 <= umbral_rssi <= 0):
            QMessageBox.warning(
                self.ui,
                "RSSI fuera de rango",
                "El umbral de RSSI debe estar entre -120 dBm y 0 dBm.",
            )
            return

        if not (-40 <= umbral_temp <= 120):
            QMessageBox.warning(
                self.ui,
                "Temperatura fuera de rango",
                "El umbral de temperatura debe estar entre -40 °C y 120 °C.",
            )
            return

        if not (1 <= ventana <= 500):
            QMessageBox.warning(
                self.ui,
                "Ventana fuera de rango",
                "La ventana del promedio móvil debe estar entre 1 y 500.",
            )
            return

        resultados, problemas = analizar_estaciones(
            self.datos, umbral_rssi, umbral_temp, ventana
        )

        self.umbral_rssi = umbral_rssi
        self.umbral_temp = umbral_temp
        self.ventana = ventana

        grafico_margen(self.ui.widget_grafico_margen, self.datos, self.umbral_rssi)

        anterior = self.ui.comboBox_estacion.currentText()
        self.ui.comboBox_estacion.blockSignals(True)
        self.ui.comboBox_estacion.clear()
        self.ui.comboBox_estacion.addItems(sorted(self.datos.keys()))
        if anterior in self.datos:
            self.ui.comboBox_estacion.setCurrentText(anterior)
        else:
            self.ui.comboBox_estacion.setCurrentIndex(0)
        self.ui.comboBox_estacion.blockSignals(False)
        self.actualizar_estacion()

        if problemas:
            self.ui.cuadro_problemas.setPlainText("\n".join(problemas))
        else:
            self.ui.cuadro_problemas.setPlainText("No se detectaron problemas.")

        lineas_ficha = []
        for est, info in resultados.items():
            bloque = (
                f"=== Estación {est} ({info['muestras']} muestras) ===\n"
                f"RSSI: prom {info['rssi_prom']:.2f} dBm | min {info['rssi_min']:.2f} | max {info['rssi_max']:.2f} | margen {info['margen_rssi']:.2f} dB\n"
                f"Temp: prom {info['temp_prom']:.2f} °C | min {info['temp_min']:.2f} | max {info['temp_max']:.2f}"
            )
            lineas_ficha.append(bloque)

        self.ui.cuadro_ficha.setPlainText("\n\n".join(lineas_ficha))

        self.ui.statusbar.showMessage("Análisis completo")

    def actualizar_estacion(self):
        estacion = self.ui.comboBox_estacion.currentText()
        if not estacion or not self.datos:
            return

        grafico_evolucion(
            self.ui.widget_grafico_evolucion,
            self.datos[estacion],
            self.umbral_rssi,
            self.umbral_temp,
            self.ventana,
        )

    def cerrar(self):
        self.datos = None
        self.ui.espacio_archivo.clear()
        limpiar_grafico(self.ui.widget_grafico_margen)
        limpiar_grafico(self.ui.widget_grafico_evolucion)
        self.ui.comboBox_estacion.clear()
        self.ui.cuadro_problemas.clear()
        self.ui.cuadro_ficha.clear()
        self.ui.statusbar.showMessage("Archivo cerrado")

    def mostrar(self):
        self.ui.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MonitorRed()
    ventana.mostrar()
    sys.exit(app.exec())
