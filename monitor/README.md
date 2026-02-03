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

Instalação (recomendado) — macOS / Linux / Windows

Siga os passos abaixo a partir da raiz do repositório (`monisystem`) para garantir que tudo funcione em qualquer sistema.

macOS / Linux

```bash
cd /path/to/monisystem
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r monitor/requirements.txt
# Execute o app a partir da raiz do projeto:
python -m monitor.main
```

Windows (PowerShell)

```powershell
cd C:\path\to\monisystem
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r monitor/requirements.txt
python -m monitor.main
```

Ou, se preferir executar a partir da pasta `monitor/`:

```bash
cd monitor
python3 -m venv .venv
source .venv/bin/activate   # (Windows: .\.venv\Scripts\Activate.ps1)
pip install -r requirements.txt
python main.py
```

Dicas:
- Use `python3` quando houver múltiplas versões (ex.: macOS/Linux).
- No macOS pode ser necessário autorizar o Terminal/Python em "Segurança e Privacidade" para que o `psutil` leia métricas do sistema.
- Se tiver problemas com a system tray, verifique suporte a app indicators/GNOME/KDE no seu sistema.

Próximos passos sugeridos:
- Adicionar preferências (intervalo configurável)
- Mostrar lista de processos e uso por processo
- Adicionar exportação CSV / gráficos históricos
- Empacotar com PyInstaller / briefcase para .app/.exe
