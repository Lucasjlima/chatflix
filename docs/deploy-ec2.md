# Deploy do Chatflix em EC2

Guia das três opções avaliadas no spec. Escolha uma. Pré-requisitos comuns aplicam a todas.

## Pré-requisitos comuns

### 1. Instância EC2

- **AMI:** Amazon Linux 2023 ou Ubuntu 22.04 LTS
- **Tipo:** `t3.micro` (free tier) ou `t3.small`
- **Storage:** 8GB gp3 padrão é suficiente

### 2. Security Group

Inbound rules:

| Tipo | Protocolo | Porta | Origem | Observação |
|---|---|---|---|---|
| SSH | TCP | 22 | seu IP | Para você administrar |
| Custom TCP | TCP | 8501 | 0.0.0.0/0 | Streamlit (público) |

### 3. SSH na instância

```bash
ssh -i sua-chave.pem ec2-user@<IP_PUBLICO>
# Ubuntu: ssh -i sua-chave.pem ubuntu@<IP_PUBLICO>
```

### 4. Instalar Python 3.11+

**Amazon Linux 2023:**

```bash
sudo dnf install -y python3.11 python3.11-pip git
```

**Ubuntu 22.04:**

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git
```

### 5. Clonar o repositório

```bash
git clone https://github.com/Lucasjlima/chatflix.git
cd chatflix
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 6. Configurar segredos

```bash
cp .env.example .env
nano .env  # preencher GEMINI_API_KEY e TMDB_API_KEY
chmod 600 .env
```

---

## Opção A: systemd service (recomendado para portfólio)

Sobrevive a reboots, logs estruturados via `journalctl`, restart automático em falha.

### 1. Criar arquivo de serviço

```bash
sudo nano /etc/systemd/system/chatflix.service
```

Conteúdo (ajuste `User` e `WorkingDirectory` conforme sua distribuição):

```ini
[Unit]
Description=Chatflix Streamlit App
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/chatflix
EnvironmentFile=/home/ec2-user/chatflix/.env
ExecStart=/home/ec2-user/chatflix/.venv/bin/streamlit run app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> No Ubuntu, troque `User=ec2-user` por `User=ubuntu` e o caminho `/home/ec2-user/` por `/home/ubuntu/`.

### 2. Ativar e iniciar

```bash
sudo systemctl daemon-reload
sudo systemctl enable chatflix
sudo systemctl start chatflix
sudo systemctl status chatflix
```

### 3. Ver logs

```bash
sudo journalctl -u chatflix -f
```

### 4. Restart após mudar código

```bash
cd ~/chatflix && git pull
sudo systemctl restart chatflix
```

---

## Opção B: tmux (mais simples para estudo)

Não sobrevive a reboots — adequado para validação rápida.

### 1. Instalar tmux

```bash
# Amazon Linux 2023
sudo dnf install -y tmux

# Ubuntu
sudo apt install -y tmux
```

### 2. Iniciar sessão e rodar

```bash
tmux new -s chatflix
cd ~/chatflix && source .venv/bin/activate
streamlit run app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
```

Sair sem matar (detach): `Ctrl+B` depois `D`.

### 3. Reconectar

```bash
tmux attach -t chatflix
```

### 4. Matar a sessão

```bash
tmux kill-session -t chatflix
```

---

## Opção C: Docker

Portátil — testa local exatamente igual EC2.

### 1. Criar `Dockerfile` na raiz do projeto

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
```

### 2. Build e run local (validação)

```bash
docker build -t chatflix .
docker run --rm -p 8501:8501 --env-file .env chatflix
```

Acesse http://localhost:8501.

### 3. Na EC2

```bash
# Amazon Linux 2023
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
# Faça logout/login para o grupo aplicar

cd ~/chatflix
docker build -t chatflix .
docker run -d --restart=always --name chatflix \
  -p 8501:8501 --env-file .env chatflix
```

### 4. Logs e restart

```bash
docker logs -f chatflix
docker restart chatflix
```

---

## Acesso

Após qualquer das opções, abra no navegador:

```
http://<IP_PUBLICO_DA_EC2>:8501
```

## HTTPS (próximos passos, fora deste MVP)

Use Caddy ou nginx + Let's Encrypt na frente do Streamlit. Caddy oferece TLS automático com um arquivo de config de 3 linhas.
