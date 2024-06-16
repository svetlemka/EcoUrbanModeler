import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QComboBox, QVBoxLayout, QWidget, \
    QFileDialog, QMessageBox, QTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Справка')
        self.setGeometry(200, 200, 600, 400)

        self.initUI()

    def initUI(self):
        help_text = """
        Для использования приложения:
        1. Загрузите CSV файлы с данными с помощью кнопки 'Загрузить файл'.
        2. Введите координаты (широта, долгота).
        3. Выберите вид загрязнения.
        4. Нажмите кнопку 'Построить модель' для визуализации модели.
        5. Для сохранения модели используйте соответствующие кнопки.
        6. Для построения новой модели нажмите на кнопку 'Сбросить модель', после чего повторите предыдущие действия.
        """

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(50, 50, 500, 300)
        self.text_edit.setPlainText(help_text)
        self.text_edit.setReadOnly(True)


class PollutionModelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Eco-climatic Model Application')
        self.setGeometry(100, 100, 1000, 800)

        # Set light green background
        self.setStyleSheet("background-color: #C3FDB8;")

        self.initUI()

        self.data_files = []  # List to store data from multiple files
        self.map_webview = None
        self.canvas = None
        self.toolbar = None

    def initUI(self):
        # Labels
        self.label_file_info = QLabel('Файлы не загружены', self)
        self.label_file_info.setGeometry(50, 50, 900, 30)

        self.label_coords = QLabel('Введите координаты (широта, долгота):', self)
        self.label_coords.setGeometry(50, 100, 250, 30)

        self.label_pollution = QLabel('Выберите вид загрязнения:', self)
        self.label_pollution.setGeometry(50, 150, 250, 30)

        # LineEdits
        self.line_edit_coords = QLineEdit(self)
        self.line_edit_coords.setGeometry(300, 100, 200, 30)
        self.line_edit_coords.setStyleSheet("background-color: white;")

        # ComboBox
        self.combo_box_pollution = QComboBox(self)
        self.combo_box_pollution.setGeometry(300, 150, 150, 30)
        self.combo_box_pollution.addItems(['nh3', 'co', 'no2', 'dust'])
        self.combo_box_pollution.setStyleSheet("background-color: white;")

        # Buttons
        self.btn_load_file = QPushButton('Загрузить файл', self)
        self.btn_load_file.setGeometry(50, 200, 150, 30)
        self.btn_load_file.setStyleSheet("background-color: white;")
        self.btn_load_file.clicked.connect(self.load_file)

        self.btn_plot_model = QPushButton('Построить модель', self)
        self.btn_plot_model.setGeometry(300, 200, 150, 30)
        self.btn_plot_model.setStyleSheet("background-color: white;")
        self.btn_plot_model.clicked.connect(self.plot_model)

        self.btn_save_model = QPushButton('Сохранить модель', self)
        self.btn_save_model.setGeometry(500, 200, 150, 30)
        self.btn_save_model.setStyleSheet("background-color: white;")
        self.btn_save_model.clicked.connect(self.save_model)

        self.btn_reset_model = QPushButton('Сбросить модель', self)
        self.btn_reset_model.setGeometry(700, 200, 150, 30)
        self.btn_reset_model.setStyleSheet("background-color: white;")
        self.btn_reset_model.clicked.connect(self.reset_model)

        # Help Button
        self.btn_help = QPushButton('Справка', self)
        self.btn_help.setGeometry(850, 20, 100, 30)
        self.btn_help.setStyleSheet("background-color: white;")
        self.btn_help.clicked.connect(self.show_help)

        # Placeholder for displaying plots
        self.plot_placeholder = QWidget(self)
        self.plot_placeholder.setGeometry(50, 250, 900, 500)

    def load_file(self):
        options = QFileDialog.Options()
        file_names, _ = QFileDialog.getOpenFileNames(self, "Выбрать CSV файлы", "", "CSV Files (*.csv)", options=options)
        if file_names:
            self.data_files = []
            for file_name in file_names:
                data = pd.read_csv(file_name, delimiter=';')
                self.data_files.append(data)
            self.label_file_info.setText(f"Загружено файлов: {len(self.data_files)}")

    def plot_model(self):
        # Clear previous plot and map widget
        self.clear_previous_plot()

        if not self.data_files:
            QMessageBox.warning(self, "Ошибка", "Файлы не загружены.")
            return

        try:
            # Get user input
            coords = self.line_edit_coords.text()
            lat, lon = map(float, coords.split(','))
            pollution_type = self.combo_box_pollution.currentText().strip()

            # Initialize variables for summation
            total_pollution_values = None

            for data in self.data_files:
                mean_pollution = data[pollution_type].mean()
                mean_wind_speed = data['ws'].mean()

                # Interpolation parameters
                k = 1.86
                x1 = lat + 0.001213
                y1 = lon + 0.000918

                # Create grid coordinates
                x = np.linspace(lat - 0.01, lat + 0.01, 100)
                y = np.linspace(lon - 0.01, lon + 0.01, 100)
                X, Y = np.meshgrid(x, y)

                # Pollution model calculation
                pollution_values = (mean_pollution / (2 * np.pi * k ** 2 * mean_wind_speed)) * np.exp(
                    -(((X - x1) ** 2 + (Y - y1) ** 2) / (2 * k ** 2)))

                # Summing pollution values from all files
                if total_pollution_values is None:
                    total_pollution_values = pollution_values
                else:
                    total_pollution_values += pollution_values

            # Plotting 3D model
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(X, Y, total_pollution_values, cmap='viridis')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_zlabel('Pollution Level')
            ax.set_title(f'{pollution_type.capitalize()} Distribution')

            # Embedding matplotlib plot into PyQt5 widget
            self.canvas = FigureCanvas(fig)
            layout = QVBoxLayout()
            layout.addWidget(self.canvas)
            self.plot_placeholder.setLayout(layout)

            # Adding standard navigation toolbar
            self.toolbar = NavigationToolbar(self.canvas, self.plot_placeholder)
            layout.addWidget(self.toolbar)
            self.canvas.draw()

            # Creating Folium map
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], popup='Выбранная точка', tooltip=f'Координаты: {lat}, {lon}').add_to(m)

            # Save map as HTML and display
            map_file = "map.html"
            m.save(map_file)

            # Displaying map using QWebEngineView (Qt5)
            self.map_webview = QWebEngineView()
            self.map_webview.setGeometry(50, 760, 900, 500)
            self.map_webview.setHtml(open(map_file, 'r', encoding='utf-8').read())
            self.map_webview.show()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при построении модели: {e}")

    def save_model(self):
        if not hasattr(self, 'canvas'):
            QMessageBox.warning(self, "Ошибка", "Модель не построена.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить модель", "", "PNG Files (*.png)", options=options)
        if file_name:
            try:
                self.canvas.figure.savefig(file_name)
                QMessageBox.information(self, "Успех", f"Модель успешно сохранена как {file_name}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при сохранении модели: {e}")

    def reset_model(self):
        # Reset all data and clear widgets
        self.clear_previous_plot()
        self.data_files = []
        self.line_edit_coords.clear()
        self.label_file_info.setText('Файлы не загружены')

    def clear_previous_plot(self):
        # Remove previous canvas, toolbar, and map web view
        if self.canvas:
            self.canvas.deleteLater()
            self.canvas = None
        if self.toolbar:
            self.toolbar.deleteLater()
            self.toolbar = None
        if self.map_webview:
            self.map_webview.deleteLater()
            self.map_webview = None

    def show_help(self):
        self.help_window = HelpWindow()
        self.help_window.show()


def main():
    app = QApplication(sys.argv)
    ex = PollutionModelApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
