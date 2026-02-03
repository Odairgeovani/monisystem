from PySide6 import QtCore, QtWidgets
from pathlib import Path
import json

CONFIG_PATH = Path(__file__).parent / 'config.json'

class SettingsDialog(QtWidgets.QDialog):
    interval_changed = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Configurações')
        self.setModal(True)
        layout = QtWidgets.QFormLayout(self)

        self.interval_spin = QtWidgets.QSpinBox()
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setSuffix(' s')

        self.tray_checkbox = QtWidgets.QCheckBox('Mostrar ícone na barra (tray)')

        layout.addRow('Intervalo de amostragem:', self.interval_spin)
        layout.addRow(self.tray_checkbox)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

        self.load()

    def load(self):
        if CONFIG_PATH.exists():
            try:
                cfg = json.loads(CONFIG_PATH.read_text())
            except Exception:
                cfg = {}
        else:
            cfg = {}
        # default 5 seconds
        interval = cfg.get('interval_seconds', 5)
        self.interval_spin.setValue(interval)
        self.tray_checkbox.setChecked(cfg.get('tray', True))

    def save(self):
        cfg = {
            'interval_seconds': self.interval_spin.value(),
            'tray': self.tray_checkbox.isChecked()
        }
        CONFIG_PATH.write_text(json.dumps(cfg))
        self.interval_changed.emit(cfg['interval_seconds'])

    def accept(self):
        self.save()
        super().accept()
