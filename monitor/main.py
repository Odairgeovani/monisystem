import sys
import time
from collections import deque
from pathlib import Path
import json

import psutil
from PySide6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from collector import sample_metrics
from db import DB
from processes import ProcessesWindow
from settings import SettingsDialog

BASE = Path(__file__).parent
DB_PATH = BASE / 'monitor.db'
ICON_PATH = BASE / 'icons' / 'tray.svg'
STYLE_PATH = BASE / 'ui' / 'style.qss'
CONFIG_PATH = BASE / 'config.json'

# load default config (interval in seconds)
_default_cfg = {'interval_seconds': 5, 'tray': True}
if CONFIG_PATH.exists():
    try:
        _default_cfg.update(json.loads(CONFIG_PATH.read_text()))
    except Exception:
        pass
SAMPLE_INTERVAL_MS = int(_default_cfg['interval_seconds'] * 1000)
HISTORY_POINTS = 120  # keep last 120 samples (~10 minutes)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Monitor de Sistema')
        self.resize(800, 480)

        # DB
        self.db = DB(DB_PATH)
        self.db.init_tables()

        # Central widget with sidebar + content area
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root_layout = QtWidgets.QHBoxLayout(central)

        # Sidebar
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(160)
        sb_layout = QtWidgets.QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(8, 8, 8, 8)

        logo = QtWidgets.QLabel('MoniSystem')
        logo.setAlignment(QtCore.Qt.AlignCenter)
        logo.setStyleSheet('font-weight:700; font-size:16px; color:#dbe7ff;')
        sb_layout.addWidget(logo)
        sb_layout.addSpacing(6)

        proc_btn = QtWidgets.QPushButton('Processos')
        proc_btn.setObjectName('processesBtn')
        proc_btn.setProperty('class', 'sidebar-btn')
        proc_btn.clicked.connect(self.show_processes)
        sb_layout.addWidget(proc_btn)

        settings_btn = QtWidgets.QPushButton('Configurações')
        settings_btn.setObjectName('settingsBtn')
        settings_btn.setProperty('class', 'sidebar-btn')
        settings_btn.clicked.connect(self.open_settings)
        sb_layout.addWidget(settings_btn)

        sb_layout.addStretch()
        root_layout.addWidget(sidebar)

        # Main content
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setSpacing(10)

        # Cards summary
        cards_row = QtWidgets.QHBoxLayout()
        cards_row.setSpacing(12)
        def mk_card(title):
            f = QtWidgets.QFrame()
            f.setProperty('class', 'card')
            f.setMinimumWidth(160)
            f.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            inner = QtWidgets.QVBoxLayout(f)
            inner.setContentsMargins(12, 8, 12, 8)
            inner.setSpacing(4)
            lbl_title = QtWidgets.QLabel(title)
            lbl_title.setProperty('class', 'card-title')
            lbl_title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            lbl_title.setWordWrap(False)
            lbl_val = QtWidgets.QLabel('--')
            lbl_val.setProperty('class', 'card-value')
            lbl_val.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            lbl_val.setWordWrap(False)
            inner.addWidget(lbl_title)
            inner.addWidget(lbl_val)
            return f, lbl_val

        cpu_card, self.cpu_val = mk_card('CPU')
        mem_card, self.mem_val = mk_card('Memória')
        net_card, self.net_val = mk_card('Rede (KB)')
        proc_card, self.proc_val = mk_card('Processos')
        for c in (cpu_card, mem_card, net_card, proc_card):
            c.setMinimumHeight(70)
            cards_row.addWidget(c, 1)
        content_layout.addLayout(cards_row)   

        # Tabs with plots / history
        self.tabs = QtWidgets.QTabWidget()
        tab_overview = QtWidgets.QWidget()
        to_layout = QtWidgets.QVBoxLayout(tab_overview)

        self.plot_widget = pg.PlotWidget(title='Métricas')
        self.plot_widget.addLegend()
        self.plot_widget.showGrid(x=True, y=True)
        self.cpu_curve = self.plot_widget.plot(pen=pg.mkPen('#ff6b6b', width=2), name='CPU %')
        self.mem_curve = self.plot_widget.plot(pen=pg.mkPen('#60a5fa', width=2), name='Mem %')
        self.net_curve = self.plot_widget.plot(pen=pg.mkPen('#34d399', width=2), name='Net (KB/s)')
        to_layout.addWidget(self.plot_widget)

        tab_history = QtWidgets.QWidget()
        th_layout = QtWidgets.QVBoxLayout(tab_history)
        self.history_table = QtWidgets.QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels(['Timestamp', 'CPU %', 'Mem %', 'Processos'])
        th_layout.addWidget(self.history_table)

        self.tabs.addTab(tab_overview, 'Visão Geral')
        self.tabs.addTab(tab_history, 'Histórico')
        content_layout.addWidget(self.tabs)

        root_layout.addWidget(content, 1)

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

        # System Tray (with settings) - visibility controlled by config
        self.tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon(str(ICON_PATH)), self)
        menu = QtWidgets.QMenu()
        show_action = menu.addAction('Mostrar')
        processes_action = menu.addAction('Processos')
        settings_action = menu.addAction('Configurações')
        quit_action = menu.addAction('Sair')
        show_action.triggered.connect(self.showNormal)
        processes_action.triggered.connect(self.show_processes)
        settings_action.triggered.connect(self.open_settings)
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_activated)
        if _default_cfg.get('tray', True):
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

    def open_settings(self):
        # create settings dialog on demand and connect
        if not hasattr(self, 'settings_dialog') or self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self)
            self.settings_dialog.interval_changed.connect(self.on_interval_changed)
        self.settings_dialog.load()
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def on_interval_changed(self, seconds: int):
        # update timer interval immediately
        try:
            ms = int(seconds) * 1000
            self.timer.setInterval(ms)
        except Exception:
            pass

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

        # Update card values and history (legacy labels removed)
        try:
            self.cpu_val.setText(f'{cpu:.1f}%')
            self.mem_val.setText(f'{mem:.1f}%')
            self.net_val.setText(f'{rate:.1f} KB/s')
            self.proc_val.setText(str(procs))
        except Exception:
            pass

        # Prepend to history table (most recent first)
        try:
            ts_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
            self.history_table.insertRow(0)
            self.history_table.setItem(0, 0, QtWidgets.QTableWidgetItem(ts_str))
            self.history_table.setItem(0, 1, QtWidgets.QTableWidgetItem(f"{cpu:.1f}"))
            self.history_table.setItem(0, 2, QtWidgets.QTableWidgetItem(f"{mem:.1f}"))
            self.history_table.setItem(0, 3, QtWidgets.QTableWidgetItem(str(procs)))
            # keep table to reasonable length
            if self.history_table.rowCount() > 500:
                self.history_table.removeRow(self.history_table.rowCount()-1)
        except Exception:
            pass

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
    # Apply stylesheet if available
    try:
        if STYLE_PATH.exists():
            app.setStyleSheet(STYLE_PATH.read_text())
    except Exception:
        pass
    app.setQuitOnLastWindowClosed(False)
    try:
        app.setWindowIcon(QtGui.QIcon(str(ICON_PATH)))
    except Exception:
        pass
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
