from PySide6 import QtCore, QtWidgets
import psutil


class ProcessesWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, refresh_ms=5000, limit=200):
        super().__init__(parent)
        self.setWindowTitle('Processos')
        self.resize(700, 400)
        layout = QtWidgets.QVBoxLayout(self)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()
        self.refresh_btn = QtWidgets.QPushButton('Atualizar')
        self.kill_btn = QtWidgets.QPushButton('Finalizar processo')
        toolbar.addWidget(self.refresh_btn)
        toolbar.addWidget(self.kill_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Table
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['PID', 'Nome', 'CPU %', 'Mem %'])
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        # Signals
        self.refresh_btn.clicked.connect(self.update_process_list)
        self.kill_btn.clicked.connect(self.kill_selected)
        self.table.doubleClicked.connect(self.on_double_click)

        self.limit = limit
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_process_list)
        self.timer.start(refresh_ms)

        # Initial population
        self.update_process_list()

    def update_process_list(self):
        procs = []
        for p in psutil.process_iter(['pid', 'name']):
            try:
                info = p.info
                # cpu_percent with interval=None uses internal psutil cache (works well for repeated calls)
                cpu = p.cpu_percent(interval=None)
                mem = p.memory_percent()
                procs.append((info['pid'], info.get('name') or '', cpu, mem))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda x: x[2], reverse=True)
        procs = procs[: self.limit]

        self.table.setRowCount(len(procs))
        for row, (pid, name, cpu, mem) in enumerate(procs):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(pid)))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(name)))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{cpu:.1f}"))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{mem:.1f}"))

    def get_selected_pid(self):
        sel = self.table.selectedItems()
        if not sel:
            return None
        row = sel[0].row()
        pid_item = self.table.item(row, 0)
        return int(pid_item.text())

    def kill_selected(self):
        pid = self.get_selected_pid()
        if pid is None:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione uma linha primeiro")
            return
        reply = QtWidgets.QMessageBox.question(self, "Confirmar", f"Finalizar processo PID {pid}?")
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait(3)
            QtWidgets.QMessageBox.information(self, "Sucesso", "Processo finalizado")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Não foi possível finalizar: {e}")
        self.update_process_list()

    def on_double_click(self, index):
        row = index.row()
        pid = int(self.table.item(row, 0).text())
        try:
            p = psutil.Process(pid)
            info = p.as_dict(attrs=[
                'pid', 'name', 'exe', 'cmdline', 'cpu_percent', 'memory_percent', 'status', 'username', 'create_time'
            ])
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Erro", f"Não foi possível acessar info do processo: {e}")
            return
        msg = "\n".join(f"{k}: {v}" for k, v in info.items())
        QtWidgets.QMessageBox.information(self, f"Processo {pid}", msg)
