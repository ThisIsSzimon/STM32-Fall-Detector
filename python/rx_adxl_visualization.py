import sys
import os
import csv
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import serial

class RealtimePlot(QtWidgets.QMainWindow):
    def __init__(self, port="COM6", baudrate=115200):
        super().__init__()
        self.setWindowTitle("Realtime ADXL345")
        
        self.ser = serial.Serial(port, baudrate, timeout=1)
        
        self.buffer_size = 200
        self.x_vals = []
        self.y_vals = []
        self.z_vals = []
        
        self.all_x = []
        self.all_y = []
        self.all_z = []
        self.all_falls = []
        
        self.sample_number = 0
        
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)
        
        self.plot_widget.addLegend()
        self.plot_widget.setYRange(-40, 40)
        self.plot_widget.setLabel('left', 'Acceleration [m/s^2]')
        self.plot_widget.setLabel('bottom', 'Sample number')
        
        self.line_x = self.plot_widget.plot(pen=pg.mkPen('r', width=2), name='X')
        self.line_y = self.plot_widget.plot(pen=pg.mkPen('g', width=2), name='Y')
        self.line_z = self.plot_widget.plot(pen=pg.mkPen('b', width=2), name='Z')
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20)

    def save_data_for_fft(self):
        """Zapisuje pełne dane od startu programu w formacie CSV"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "adxl_data_fft.csv")
        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["X", "Y", "Z", "FALL"])
            for x, y, z, fall in zip(self.all_x, self.all_y, self.all_z, getattr(self, "all_falls", [])):
                writer.writerow([x, y, z, fall])
        print(f"[INFO] Dane zapisane do {filename} ({len(self.all_x)} próbek)")

    def update(self):
        while self.ser.in_waiting:
            line = self.ser.readline().decode('utf-8').strip()
            if not line:
                continue

            if line == "STOP":
                print("[INFO] Otrzymano STOP z STM32")
                self.save_data_for_fft()
                self.timer.stop()
                return

            if line == "FALL DETECTED!":
                print("[INFO] Wykryto upadek")
                if self.all_x:  
                    self.all_falls[-1] = 1
                continue

            try:
                x_str, y_str, z_str = line.split()
                x = float(x_str)
                y = float(y_str)
                z = float(z_str)
            except ValueError:
                continue
            
            self.x_vals.append(x)
            self.y_vals.append(y)
            self.z_vals.append(z)
            
            self.all_x.append(x)
            self.all_y.append(y)
            self.all_z.append(z)
            self.all_falls.append(0)
            
            self.sample_number += 1
            
            if len(self.x_vals) > self.buffer_size:
                self.x_vals.pop(0)
                self.y_vals.pop(0)
                self.z_vals.pop(0)
            
        if self.x_vals:
            x_axis = list(range(self.sample_number - len(self.x_vals) + 1, self.sample_number + 1))
            self.line_x.setData(x_axis, self.x_vals)
            self.line_y.setData(x_axis, self.y_vals)
            self.line_z.setData(x_axis, self.z_vals)
            self.plot_widget.setXRange(x_axis[0], x_axis[-1])

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RealtimePlot()
    window.show()
    sys.exit(app.exec_())
