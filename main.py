import os
import sys
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from datos_csv import cargar_csv
from graficos import grafico_margen, grafico_evolucion


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
                "Parametros inválidos",
                "Ingresá numeros válidos (RSSI y temperatura en decimales y ventana enteros.) ",
            )
            return

        self.umbral_rssi = umbral_rssi
        self.umbral_temp = umbral_temp
        self.ventana = ventana

        grafico_margen(self.ui.widget_grafico_margen, self.datos, self.umbral_rssi)

        self.ui.comboBox_estacion.clear()
        self.ui.comboBox_estacion.addItems(sorted(self.datos.keys()))

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

    def mostrar(self):
        self.ui.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MonitorRed()
    ventana.mostrar()
    sys.exit(app.exec())
