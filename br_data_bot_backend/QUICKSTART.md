# Quick Start - BR Data Bot

Inicie o bot em 5 minutos!

## 1. Clonar e Configurar

```bash
git clone https://github.com/seu-usuario/br_data_bot.git
cd br_data_bot_backend
cp .env.example .env
```

## 2. Editar .env

```bash
nano .env
```

Configurações mínimas obrigatórias:

```env
TELEGRAM_BOT_TOKEN=seu_token_telegram
WHATSAPP_API_TOKEN=seu_token_whatsapp
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=seu_token_verificacao
```

## 3. Iniciar com Docker Compose

```bash
docker-compose up -d
```

## 4. Verificar Status

```bash
docker-compose ps
docker-compose logs -f backend
```

## 5. Testar Health Check

```bash
curl http://localhost:8000/api/health
```

## 6. Configurar Webhooks

### Telegram

```bash
curl -X POST https://api.telegram.org/botTOKEN/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://seu-dominio.com/api/webhook/telegram"}'
```

### WhatsApp

1. Acesse https://developers.facebook.com/
2. Configure webhook em sua aplicação WhatsApp
3. URL: `https://seu-dominio.com/api/webhook/whatsapp`
4. Token: valor de `WHATSAPP_WEBHOOK_VERIFY_TOKEN`

## 7. Acessar Painel Admin

```
URL: http://localhost:8000/api/admin/dashboard
Username: admin (ou seu username)
Password: admin123 (ou sua senha)
```

## Comandos Úteis

```bash
# Ver logs
docker-compose logs -f backend

# Parar aplicação
docker-compose down

# Reiniciar
docker-compose restart backend

# Acessar banco de dados
docker-compose exec postgres psql -U br_data_bot -d br_data_bot

# Resetar rate limit de um usuário
docker-compose exec redis redis-cli DEL rate_limit:telegram:USER_ID
```

## Próximos Passos

1. Leia [README.md](README.md) para documentação completa
2. Leia [DEPLOY.md](DEPLOY.md) para deploy em produção
3. Configure as APIs externas (Portal da Transparência, Have I Been Pwned)
4. Customize as mensagens em `config.py`

## Suporte

- Documentação: [README.md](README.md)
- Deploy: [DEPLOY.md](DEPLOY.md)
- Issues: GitHub Issues
- Email: admin@example.com

---

**Pronto para usar! 🚀**
