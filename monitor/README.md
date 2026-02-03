# Monitor de Sistema — App de Desktop (PySide6)

Esqueleto de um app de desktop para macOS/Linux/Windows usando Python.

Métricas coletadas por padrão:
- CPU (%)
- Memória (%)
- Rede (bytes enviados/recebidos)
- Quantidade de processos

Config:
- Intervalo de amostragem: 5 segundos
- Histórico salvo em SQLite (`monitor.db`)
- Ícone na barra (system tray / menubar)

Instalação (macOS):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Próximos passos sugeridos:
- Adicionar preferências (intervalo configurável)
- Mostrar lista de processos e uso por processo
- Adicionar exportação CSV / gráficos históricos
- Empacotar com PyInstaller / briefcase para .app/.exe
