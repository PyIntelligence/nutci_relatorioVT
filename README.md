# NUTCI — Relatório de Visita Técnica (PWA Flask + PostgreSQL Neon.tech + Render.com)

Sistema Web Progressivo (**PWA**) desenvolvido em **Python / Flask** integrado ao **PostgreSQL (Neon.tech)** e pronto para deploy no **Render.com**, espelhando fielmente o documento **`Relatorio visita técnica novo.docx`** da **3ª Gerência Regional de Educação (NUTCI / SEE-PB)**.

---

## O que foi ajustado nesta versão

1. **`requirements.txt` compatível com Windows e Render.com**: Usa `psycopg[binary]>=3.2.10`, `waitress` no Windows e `gunicorn` no Linux/Render.
2. **PDF e Impressão Fiel ao Word (HTML/CSS/JS puro)**: Na tela de visualização do relatório, basta clicar em **Gerar PDF / Imprimir (A4)** para salvar em PDF (pronto para enviar por e-mail) ou imprimir diretamente em folha A4 sem dependências externas.
3. **Equipe NUTCI + Assinatura Gov.br ou Física**:
   - Seleção rápida dos técnicos **Guega, Jairo, João Paulo, Valdênio e Isaque** (ou outro técnico), com o nome impresso logo abaixo da linha de assinatura.
   - Botão de acesso direto ao **Assinador Eletrônico Gov.br (`assinador.iti.br`)** para assinar o PDF digitalmente, mantendo o espaço limpo caso prefiram imprimir e assinar à caneta.
4. **PostgreSQL Neon.tech seguro via `.env`**: Nenhuma senha fica no código; localmente usa `.env` e no Render usa *Environment Variables*.
5. **Botão pronto para o Portal `see3gre`**: Rota `/integracao-portal` com imagens PNG/SVG prontas (`botao_see3gre.png`, `botao_see3gre.svg`, `icon-192.png`) e snippet HTML/CSS pronto para colar no portal da 3ª GRE.

---

## Como Rodar Localmente no Windows (CMD)

```cmd
python -m venv venv
venv\Scripts\activate
pip install --index-url https://pypi.org/simple -r requirements.txt
copy .env.example .env
notepad .env
python run.py
```

---

## Como Fazer Deploy no Render.com

1. Suba esta pasta para um repositório no **GitHub** (o `.gitignore` já bloqueia o envio do `.env`).
2. No painel do **Render.com**, clique em **New + > Web Service** e conecte o repositório (ou use o arquivo `render.yaml` incluso).
3. Em **Environment > Environment Variables**, adicione:
   - `DATABASE_URL`: cole a string de conexão do seu banco **Neon.tech** (`postgresql://...?sslmode=require`).
   - `SECRET_KEY`: uma chave secreta aleatória.
   - `FLASK_ENV`: `production`
4. Clique em **Deploy Web Service**.
