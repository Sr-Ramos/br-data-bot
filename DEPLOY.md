# Guia de Deploy - BR Data Bot

Este documento fornece instruções detalhadas para fazer deploy do BR Data Bot em produção.

## 📋 Pré-requisitos

- Servidor Linux (Ubuntu 20.04 LTS recomendado)
- Docker e Docker Compose instalados
- Domínio com HTTPS configurado
- Tokens de API configurados:
  - Telegram Bot Token
  - WhatsApp API Token
  - Portal da Transparência Token (opcional)
  - Have I Been Pwned API Key (opcional)

## 🚀 Deploy em VPS

### 1. Preparar o Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Adicionar seu usuário ao grupo docker (opcional)
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clonar o Repositório

```bash
# Criar diretório para o projeto
mkdir -p /opt/br_data_bot
cd /opt/br_data_bot

# Clonar repositório
git clone https://github.com/seu-usuario/br_data_bot.git .
```

### 3. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas credenciais
nano .env
```

Configurações importantes:

```env
# Segurança
DEBUG=False
ADMIN_SECRET_KEY=gerar-chave-segura-aqui

# Banco de Dados
DB_USER=br_data_bot
DB_PASSWORD=gerar-senha-segura-aqui
DB_NAME=br_data_bot

# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_WEBHOOK_URL=https://seu-dominio.com/api/webhook/telegram

# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id
WHATSAPP_BUSINESS_ACCOUNT_ID=seu_business_account_id
WHATSAPP_API_TOKEN=seu_token_aqui
WHATSAPP_WEBHOOK_URL=https://seu-dominio.com/api/webhook/whatsapp
WHATSAPP_WEBHOOK_VERIFY_TOKEN=gerar-token-seguro-aqui

# APIs Externas
PORTAL_TRANSPARENCIA_TOKEN=seu_token_aqui
HAVE_I_BEEN_PWNED_API_KEY=sua_api_key

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=gerar-senha-segura-aqui
```

### 4. Configurar Nginx como Reverse Proxy

```bash
# Instalar Nginx
sudo apt install nginx -y

# Criar configuração
sudo nano /etc/nginx/sites-available/br_data_bot
```

Adicione:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com;
    
    # Certificados SSL (usar Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    # Configurações SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Proxy para FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
    
    # Logs
    access_log /var/log/nginx/br_data_bot_access.log;
    error_log /var/log/nginx/br_data_bot_error.log;
}
```

Ativar site:

```bash
sudo ln -s /etc/nginx/sites-available/br_data_bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Configurar SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Gerar certificado
sudo certbot certonly --nginx -d seu-dominio.com

# Renovação automática
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 6. Iniciar Aplicação com Docker Compose

```bash
# Construir imagens
docker-compose build

# Iniciar serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f backend
```

### 7. Configurar Webhooks

#### Telegram

```bash
# Substituir TOKEN e URL
curl -X POST https://api.telegram.org/botTOKEN/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://seu-dominio.com/api/webhook/telegram"}'

# Verificar webhook
curl -X GET https://api.telegram.org/botTOKEN/getWebhookInfo
```

#### WhatsApp

1. Acesse https://developers.facebook.com/
2. Selecione sua aplicação WhatsApp
3. Vá para "Configurações" > "Webhooks"
4. Configure:
   - **URL do Callback**: `https://seu-dominio.com/api/webhook/whatsapp`
   - **Token de Verificação**: o valor em `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
5. Selecione os eventos: `messages`, `message_status`

### 8. Monitoramento e Manutenção

#### Systemd Service (opcional)

Criar arquivo `/etc/systemd/system/br-data-bot.service`:

```ini
[Unit]
Description=BR Data Bot
After=docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=/opt/br_data_bot
ExecStart=/usr/local/bin/docker-compose up
ExecStop=/usr/local/bin/docker-compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ativar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable br-data-bot
sudo systemctl start br-data-bot
```

#### Backups

```bash
# Backup do banco de dados
docker-compose exec postgres pg_dump -U br_data_bot br_data_bot > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T postgres psql -U br_data_bot br_data_bot < backup_20240101.sql
```

#### Logs

```bash
# Ver logs em tempo real
docker-compose logs -f backend

# Logs do Nginx
sudo tail -f /var/log/nginx/br_data_bot_access.log
sudo tail -f /var/log/nginx/br_data_bot_error.log

# Logs da aplicação
docker-compose exec backend tail -f logs/app.log
```

## 🔒 Segurança em Produção

### Checklist de Segurança

- [ ] DEBUG=False em .env
- [ ] Senhas fortes para admin e banco de dados
- [ ] HTTPS configurado e ativo
- [ ] Firewall configurado (apenas portas 80, 443)
- [ ] Backups automáticos configurados
- [ ] Rate limiting ativado
- [ ] Logs monitorados regularmente
- [ ] Atualizações de segurança aplicadas

### Firewall (UFW)

```bash
# Ativar UFW
sudo ufw enable

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar regras
sudo ufw status
```

### Backup Automático

Criar script `/opt/br_data_bot/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/br_data_bot/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup do banco de dados
cd /opt/br_data_bot
docker-compose exec -T postgres pg_dump -U br_data_bot br_data_bot | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup realizado: $BACKUP_DIR/db_$DATE.sql.gz"
```

Adicionar ao crontab:

```bash
# Backup diário às 2 da manhã
0 2 * * * /opt/br_data_bot/backup.sh
```

## 📊 Monitoramento

### Health Check

```bash
# Verificar saúde da aplicação
curl https://seu-dominio.com/api/health

# Resposta esperada:
# {"status":"healthy","timestamp":"2024-01-15T10:30:00.000000","service":"br-data-bot"}
```

### Métricas

Implementar monitoramento com Prometheus/Grafana (opcional):

```bash
# Instalar Prometheus
docker pull prom/prometheus

# Configurar scrape de métricas FastAPI
# Adicionar em prometheus.yml:
# - job_name: 'br_data_bot'
#   static_configs:
#     - targets: ['localhost:8000']
```

## 🐛 Troubleshooting

### Aplicação não inicia

```bash
# Verificar logs
docker-compose logs backend

# Verificar se porta está em uso
sudo lsof -i :8000

# Reiniciar serviços
docker-compose restart
```

### Erro de conexão com banco de dados

```bash
# Verificar status do PostgreSQL
docker-compose ps postgres

# Verificar logs
docker-compose logs postgres

# Reiniciar PostgreSQL
docker-compose restart postgres
```

### Webhook não funciona

```bash
# Verificar se URL é acessível
curl -I https://seu-dominio.com/api/webhook/telegram

# Verificar logs do Nginx
sudo tail -f /var/log/nginx/br_data_bot_error.log

# Testar webhook manualmente
curl -X POST https://seu-dominio.com/api/webhook/telegram \
  -H "Content-Type: application/json" \
  -d '{"update_id":1,"message":{"message_id":1,"from":{"id":123,"is_bot":false,"first_name":"Test"},"text":"/start"}}'
```

## 📈 Escalabilidade

Para aumentar a capacidade:

1. **Aumentar workers Uvicorn**:
   ```bash
   # Em main.py ou docker-compose.yml
   uvicorn main:app --workers 4
   ```

2. **Load Balancing com Nginx**:
   ```nginx
   upstream backend {
       server 127.0.0.1:8000;
       server 127.0.0.1:8001;
       server 127.0.0.1:8002;
   }
   ```

3. **Aumentar recursos do PostgreSQL**:
   ```yaml
   # docker-compose.yml
   postgres:
     environment:
       POSTGRES_SHARED_BUFFERS: 256MB
       POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
   ```

## 📞 Suporte

Para problemas durante o deploy:
- Verifique os logs: `docker-compose logs`
- Consulte a documentação do FastAPI
- Abra uma issue no GitHub

---

**Última atualização**: 2024-01-15
