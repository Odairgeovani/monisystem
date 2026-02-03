# monisystem — Monitor de Sistema 🖥️

**Resumo:**
Monitor de atividades do sistema em formato de **app de desktop** (Python + PySide6) que coleta métricas e salva um histórico local em SQLite. Funciona em **macOS, Linux e Windows** para uso local e prototipagem rápida.

---

## 🔍 O que ele monitora
- CPU (%)
- Memória (%)
- Rede (bytes enviados / recebidos)
- Quantidade de processos

Dados são gravados em **SQLite** no arquivo `monitor/monitor.db`.

---

## ⚙️ Como ele funciona (resumo técnico)
- `monitor/collector.py` usa a biblioteca **psutil** para ler métricas do sistema.
- `monitor/db.py` armazena amostras na tabela `metrics` (timestamp, cpu, mem, net_sent, net_recv, processes).
- `monitor/main.py` é a aplicação PySide6 (UI), plota gráficos com **pyqtgraph**, mostra sumário e permite abrir a lista de processos.

---

## ▶️ Guia rápido de execução (multi‑plataforma)
Abra um terminal na pasta do projeto e siga os passos para seu sistema.

macOS / Linux

```bash
cd /path/to/monisystem
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r monitor/requirements.txt
python3 monitor/main.py
```

Windows (PowerShell)

```powershell
cd C:\path\to\monisystem
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r monitor/requirements.txt
python monitor\main.py
```

Dica: se o `python` do sistema for Python 2 ou houver múltiplas versões, prefira `python3` quando disponível.

---

## 🧭 Como usar a interface
- Ao abrir, você verá no topo **resumos** (CPU, Memória, Rede, Processos).
- O gráfico principal mostra histórico das métricas (últimos ~10 minutos por padrão).
- Clique em **Ver Processos** para abrir a janela com a lista de processos (ordenável, permite ver detalhes e encerrar um processo).
- Um ícone ficará disponível na **system tray / menubar**: use-o para abrir o app ou sair.

Para alterar o intervalo de amostragem, edite `SAMPLE_INTERVAL_MS` em `monitor/main.py` (valor em milissegundos).

---

## 🗄️ Inspecionar o histórico (SQLite)
O banco `monitor/monitor.db` contém a tabela `metrics`. Para ver as últimas linhas:

```bash
sqlite3 monitor/monitor.db "SELECT timestamp, cpu, mem, net_sent, net_recv, processes FROM metrics ORDER BY timestamp DESC LIMIT 10;"
```

---

## ⚠️ Solução de problemas comuns
- Erros de importação: certifique‑se de ativar o virtualenv e executar `python -m pip install -r monitor/requirements.txt`.
- macOS: pode ser necessário autorizar o Terminal ou Python em **Preferências do Sistema > Segurança e Privacidade** para acessar dados do sistema (psutil).
- Linux: alguns ambientes podem precisar de suporte a ícones de system tray (por ex. libappindicator). Se o ícone não aparecer, verifique o ambiente gráfico.
- Se o app não iniciar, execute `python3 monitor/main.py` e confira as mensagens/traceback no terminal.

---

## 📦 Empacotamento (opcional)
Para distribuir como aplicativo:
- PyInstaller (ex.: `pyinstaller --onefile --add-data "monitor/icons:monitor/icons" monitor/main.py`)
- briefcase / Briefcase/PyOxidizer para builds multiplataforma

Lembre‑se de testar o comportamento da system tray e permissões no sistema alvo antes de distribuir.

---

## ⚙️ Desenvolvimento e contribuições
- Código-fonte: `monitor/` contém os módulos principais (`main.py`, `collector.py`, `db.py`, `processes.py`).
- Se quiser que eu adicione filtros na lista de processos, preferências para intervalo ou empacotamento do app, diga o que prefere e eu implemento.

---

## 📞 Contato / Ajuda
Abra uma issue no repositório com detalhes do problema (logs, sistema operacional, versão do Python) e eu te ajudo a resolver.

---

**Pronto para eu adicionar uma seção de empacotamento (com um script PyInstaller) ou prefere que eu implemente filtros na janela de processos primeiro?**
