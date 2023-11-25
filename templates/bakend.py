# ... (previous imports and classes)
import sys
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime
import speedtest
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QThread

class Communicate(QObject):
    update_speed = pyqtSignal(float, float, float)
    plot_graph = pyqtSignal(str, float, str)

class BandwidthMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.label_download = QLabel("Download Speed: N/A", self)
        self.layout.addWidget(self.label_download)

        self.label_upload = QLabel("Upload Speed: N/A", self)
        self.layout.addWidget(self.label_upload)

        self.label_latency = QLabel("Latency: N/A", self)
        self.layout.addWidget(self.label_latency)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.start_button = QPushButton("Start Monitoring", self)
        self.start_button.clicked.connect(self.start_monitoring)
        self.layout.addWidget(self.start_button)

        self.speedtest_thread = SpeedtestThread()
        self.speedtest_thread.communicate.update_speed.connect(self.update_speed_labels)
        self.speedtest_thread.communicate.plot_graph.connect(self.plot_graph)

    def update_speed_labels(self, download_speed, upload_speed, latency):
        self.label_download.setText(f"Download Speed: {download_speed:.2f} Mbps")
        self.label_upload.setText(f"Upload Speed: {upload_speed:.2f} Mbps")
        self.label_latency.setText(f"Latency: {latency:.2f} ms")

    def plot_graph(self, x, y, label):
        self.ax.plot(x, y, label=label)
        self.ax.legend()
        self.canvas.draw()

    def start_monitoring(self):
        self.speedtest_thread.start()

    def closeEvent(self, event):
        self.speedtest_thread.stop()
        event.accept()

class SpeedtestThread(QThread):
    def __init__(self):
        super().__init__()
        self.communicate = Communicate()
        self.running = False

    def run(self):
        self.running = True
        st = speedtest.Speedtest()

        while self.running:
            try:
                download_speed = st.download() / 10**6  # Convert to Mbps
                upload_speed = st.upload() / 10**6  # Convert to Mbps
                latency = st.results.ping  # Latency in milliseconds

                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")

                self.communicate.update_speed.emit(download_speed, upload_speed, latency)
                self.communicate.plot_graph.emit(current_time, download_speed, "Download Speed")
                self.communicate.plot_graph.emit(current_time, upload_speed, "Upload Speed")
            except speedtest.SpeedtestBestServerFailure as e:
                print(f"Error getting best server: {e}")
                # Handle the error as needed (e.g., show an error message in the UI)

            self.msleep(1000)  # Sleep for 0.5 seconds

    def stop(self):
        self.running = False
        self.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BandwidthMonitor()
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle("Bandwidth Monitor")
    window.show()
    sys.exit(app.exec_())
