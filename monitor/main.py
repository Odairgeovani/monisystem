import sys
import time
from collections import deque
from pathlib import Path

import psutil
from PySide6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from collector import sample_metrics
from db import DB
from processes import ProcessesWindow

BASE = Path(__file__).parent
DB_PATH = BASE / 'monitor.db'
ICON_PATH = BASE / 'icons' / 'tray.svg'

SAMPLE_INTERVAL_MS = 5000  # 5 seconds
HISTORY_POINTS = 120  # keep last 120 samples (~10 minutes)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Monitor de Sistema')
        self.resize(800, 480)

        # DB
        self.db = DB(DB_PATH)
        self.db.init_tables()

        # Central widget
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Top summary
        summary_layout = QtWidgets.QHBoxLayout()
        self.cpu_label = QtWidgets.QLabel('CPU: --%')
        self.mem_label = QtWidgets.QLabel('Memória: --%')
        self.net_label = QtWidgets.QLabel('Rede: sent=-- recv=--')
        self.proc_label = QtWidgets.QLabel('Processos: --')
        for w in (self.cpu_label, self.mem_label, self.net_label, self.proc_label):
            w.setMinimumWidth(180)
            summary_layout.addWidget(w)
        proc_btn = QtWidgets.QPushButton('Ver Processos')
        proc_btn.clicked.connect(self.show_processes)
        summary_layout.addWidget(proc_btn)
        summary_layout.addStretch()
        layout.addLayout(summary_layout)

        # Prepare processes window (created on demand)
        self.process_window = None

        # Plots
        self.plot_widget = pg.PlotWidget(title='Métricas')
        self.plot_widget.addLegend()
        self.plot_widget.showGrid(x=True, y=True)
        self.cpu_curve = self.plot_widget.plot(pen=pg.mkPen('r', width=2), name='CPU %')
        self.mem_curve = self.plot_widget.plot(pen=pg.mkPen('b', width=2), name='Mem %')
        self.net_curve = self.plot_widget.plot(pen=pg.mkPen('g', width=2), name='Net (KB/s)')
        layout.addWidget(self.plot_widget)

        # Data buffers
        self.timestamps = deque(maxlen=HISTORY_POINTS)
        self.cpu_data = deque(maxlen=HISTORY_POINTS)
        self.mem_data = deque(maxlen=HISTORY_POINTS)
        self.net_rate_data = deque(maxlen=HISTORY_POINTS)
        self._last_net = None
        self._last_time = None

        # Timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(SAMPLE_INTERVAL_MS)

        # System Tray
        self.tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon(str(ICON_PATH)), self)
        menu = QtWidgets.QMenu()
        show_action = menu.addAction('Mostrar')
        processes_action = menu.addAction('Processos')
        quit_action = menu.addAction('Sair')
        show_action.triggered.connect(self.showNormal)
        processes_action.triggered.connect(self.show_processes)
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

        # Initial update
        QtCore.QTimer.singleShot(100, self.update_metrics)

    def on_tray_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.showNormal()

    def show_processes(self):
        if self.process_window is None:
            self.process_window = ProcessesWindow(self)
        self.process_window.show()
        self.process_window.raise_()
        self.process_window.activateWindow()

    def update_metrics(self):
        data = sample_metrics()
        ts = data['timestamp']
        cpu = data['cpu']
        mem = data['mem']
        net_sent = data['net_sent']
        net_recv = data['net_recv']
        procs = data['processes']

        # Calculate network rate (KB/s)
        rate = 0.0
        if self._last_net is not None and self._last_time is not None:
            dt = ts - self._last_time
            if dt > 0:
                bytes_diff = (net_sent + net_recv) - self._last_net
                rate = (bytes_diff / dt) / 1024.0
        self._last_net = net_sent + net_recv
        self._last_time = ts

        # Update labels
        self.cpu_label.setText(f'CPU: {cpu:.1f}%')
        self.mem_label.setText(f'Memória: {mem:.1f}%')
        self.net_label.setText(f'Rede: sent={net_sent} recv={net_recv}')
        self.proc_label.setText(f'Processos: {procs}')

        # Append data
        self.timestamps.append(ts)
        self.cpu_data.append(cpu)
        self.mem_data.append(mem)
        self.net_rate_data.append(rate)

        # Update plots
        x = list(range(-len(self.timestamps)+1, 1))
        self.cpu_curve.setData(x, list(self.cpu_data))
        self.mem_curve.setData(x, list(self.mem_data))
        self.net_curve.setData(x, list(self.net_rate_data))

        # Persist to DB
        try:
            self.db.insert_sample(ts, cpu, mem, net_sent, net_recv, procs)
        except Exception as e:
            print('DB insert error:', e)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
