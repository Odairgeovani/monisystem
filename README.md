# monisystem — Monitor de Sistema 🖥️

**Resumo:**
Monitor de atividades do sistema em formato de **app de desktop** (Python + PySide6) que coleta métricas e salva um histórico local em SQLite. É um protótipo leve pensado para macOS/Linux/Windows.

---

## 🔍 O que ele faz
- Coleta: **CPU (%)**, **Memória (%)**, **Rede** (bytes enviados/recebidos) e **Quantidade de processos**.
- Armazena histórico em **SQLite** (`monitor/monitor.db`).
- Atualização padrão a cada **5 segundos**.
- Interface gráfica com gráficos em tempo real (pyqtgraph) e ícone na **system tray / menubar**.

---

## ⚙️ Como funciona (breve)
- `collector.py` usa **psutil** para ler métricas do sistema.
- `db.py` grava amostras na tabela `metrics` do arquivo SQLite.
- `main.py` é a aplicação PySide6 que exibe os valores em tempo real, plota gráficos e persiste amostras.

---

## ▶️ Como executar (macOS)
1. Abra o Terminal na pasta do projeto:

```bash
cd /Users/odair/Desktop/monisystem
```

2. (Opcional, recomendado) crie e ative um virtualenv:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instale dependências:

```bash
python3 -m pip install -r monitor/requirements.txt
```

4. Rode a aplicação:

```bash
python3 monitor/main.py
```

O ícone deverá aparecer na barra; clique nele para abrir o app. O arquivo de banco será criado automaticamente em `monitor/monitor.db`.

---

## 📝 Arquivos importantes
- `monitor/main.py` — UI principal (PySide6 + pyqtgraph)
- `monitor/collector.py` — coleta de métricas (psutil)
- `monitor/db.py` — operações com SQLite
- `monitor/requirements.txt` — dependências
- `monitor/icons/tray.svg` — ícone para a tray

---

## ⚠️ Dicas e resolução de problemas
- Se faltar alguma dependência, execute: `python3 -m pip install -r monitor/requirements.txt`.
- Em macOS, pode ser necessário permitir o acesso a informações do sistema para que psutil recupere certos dados (ver Preferências do Sistema > Segurança & Privacidade).
- Se a tray não aparecer: verifique logs no terminal onde rodou `python3 monitor/main.py` e confirme que o aplicativo não fechou com um erro.

---

## 🚀 Próximos passos sugeridos
- Adicionar janela com **lista detalhada de processos** e ordenação por CPU/memória.
- Preferências (intervalo, itens a persistir, rotações de DB).
- Empacotar com **PyInstaller** ou ferramentas de empacotamento nativas para criar um `.app`/`.exe`.

---

Se quiser, eu posso **adicionar a janela de processos** agora ou **tornar o intervalo configurável** — qual prefere? ✅
