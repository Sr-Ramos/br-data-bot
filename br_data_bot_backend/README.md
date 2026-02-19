# BR Data Bot - Consulta de Dados Públicos Brasileiros

Um bot profissional para Telegram e WhatsApp que permite consultas de dados públicos e legais no Brasil, utilizando exclusivamente APIs oficiais e bases governamentais autorizadas.

## 🎯 Objetivo

Desenvolver um sistema de consulta de dados públicos acessível via Telegram e WhatsApp, focado em transparência, conformidade legal e proteção de privacidade. O bot consulta exclusivamente informações públicas disponibilizadas por órgãos governamentais brasileiros.

## ✨ Funcionalidades

### 1. Consulta CNPJ
- Consultar dados cadastrais de empresas
- Situação fiscal e legal
- Informações de sócios
- Atividades econômicas
- Endereço e contato
- Fonte: BrasilAPI (Receita Federal)

### 2. Portal da Transparência
- Consultar vínculos públicos por CPF
- Consultar valores recebidos por CPF/CNPJ
- Informações sobre servidores públicos
- Dados de benefícios públicos (Bolsa Família, Auxílio Brasil, etc)
- Fonte: API oficial do Portal da Transparência

### 3. Dados Veiculares
- Redirecionamento para sistemas oficiais (SINESP, CDT, Detran)
- Sem armazenamento de dados sensíveis
- Links diretos para consultas oficiais

### 4. Verificação de Dados Vazados
- Verificar se email foi vazado na internet
- Informações sobre breaches de segurança
- Recomendações de segurança
- Fonte: Have I Been Pwned API

### 5. Segurança
- Rate limiting por usuário
- Bloqueio de usuários abusivos
- Logs anonimizados (sem dados pessoais)
- Validação rigorosa de entrada
- HTTPS obrigatório
- Aviso obrigatório de termos de uso

### 6. Painel Administrativo
- Dashboard com estatísticas de uso
- Gerenciamento de usuários bloqueados
- Visualização de logs anonimizados
- Configuração de rate limits
- Autenticação básica HTTP

## 🏗️ Arquitetura

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Banco de Dados**: PostgreSQL
- **Cache**: Redis
- **Bots**: python-telegram-bot, Meta Cloud API / Twilio
- **Containerização**: Docker & Docker Compose

### Estrutura de Diretórios

```
br_data_bot_backend/
├── config.py                 # Configurações centralizadas
├── models.py                 # Modelos de dados (SQLAlchemy)
├── database.py               # Gerenciamento de BD
├── security.py               # Rate limiting, hashing, validações
├── logging_config.py         # Logging anonimizado
├── external_apis.py          # Clientes para APIs externas
├── main.py                   # Aplicação FastAPI principal
├── telegram_handler.py       # Handler para Telegram
├── whatsapp_handler.py       # Handler para WhatsApp
├── routers/
│   ├── health_router.py      # Health checks
│   ├── telegram_router.py    # Webhook Telegram
│   ├── whatsapp_router.py    # Webhook WhatsApp
│   └── admin_router.py       # Painel administrativo
├── services/
│   ├── cnpj_service.py       # Serviço de consulta CNPJ
│   ├── transparencia_service.py  # Serviço Portal da Transparência
│   ├── veicular_service.py   # Serviço de dados veiculares
│   └── breach_service.py     # Serviço de dados vazados
├── Dockerfile                # Imagem Docker
├── docker-compose.yml        # Orquestração de serviços
├── requirements.txt          # Dependências Python
└── .env.example              # Variáveis de ambiente (exemplo)
```

## 🚀 Instalação e Deploy

### Pré-requisitos
- Docker e Docker Compose instalados
- Tokens de API configurados (Telegram, WhatsApp, etc)
- Domínio com HTTPS para webhooks

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/br_data_bot.git
cd br_data_bot_backend
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost:5432/br_data_bot

# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_WEBHOOK_URL=https://seu-dominio.com/webhook/telegram

# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id
WHATSAPP_API_TOKEN=seu_token_aqui
WHATSAPP_WEBHOOK_VERIFY_TOKEN=seu_token_verificacao

# APIs Externas
PORTAL_TRANSPARENCIA_TOKEN=seu_token_aqui
HAVE_I_BEEN_PWNED_API_KEY=sua_api_key

# Painel Administrativo
ADMIN_USERNAME=admin
ADMIN_PASSWORD=senha_segura
ADMIN_SECRET_KEY=chave_secreta_muito_segura
```

### 3. Iniciar com Docker Compose

```bash
# Construir e iniciar os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f backend

# Parar os serviços
docker-compose down
```

### 4. Inicializar Banco de Dados

```bash
# Conectar ao container do backend
docker-compose exec backend bash

# Dentro do container, executar:
python -c "from database import init_db; init_db()"
```

### 5. Configurar Webhooks

#### Telegram
```bash
# Substituir TOKEN e URL
curl -X POST https://api.telegram.org/botTOKEN/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://seu-dominio.com/api/webhook/telegram"}'
```

#### WhatsApp
Configure através do Meta Business Platform:
1. Acesse https://developers.facebook.com/
2. Vá para sua aplicação WhatsApp
3. Configure o webhook em "Configurações" > "Webhooks"
4. URL: `https://seu-dominio.com/api/webhook/whatsapp`
5. Token de verificação: o valor configurado em `WHATSAPP_WEBHOOK_VERIFY_TOKEN`

## 📖 Uso

### Telegram

Inicie uma conversa com o bot usando `/start`:

```
/start              - Iniciar o bot
/ajuda              - Mostrar ajuda
/consulta_cnpj      - Consultar CNPJ
/transparencia      - Consultar Portal da Transparência
/veicular           - Consultar dados veiculares
/dados_vazados      - Verificar dados vazados
/menu               - Mostrar menu principal
```

### WhatsApp

Envie uma mensagem com os mesmos comandos acima.

## 🔐 Segurança

### Conformidade Legal
- **LGPD**: Não armazenamos dados pessoais sensíveis
- **Lei de Acesso à Informação**: Usamos apenas dados públicos
- **Termos de Uso**: Aviso obrigatório antes de qualquer consulta
- **Privacidade**: Logs anonimizados, sem rastreamento pessoal

### Medidas de Segurança
- **Rate Limiting**: Limite de requisições por usuário (configurável)
- **Bloqueio de Usuários**: Bloqueio automático de usuários abusivos
- **Validação de Entrada**: Validação rigorosa de CPF, CNPJ, email
- **Logs Anonimizados**: Hashing de IDs de usuário e IP
- **HTTPS Obrigatório**: Todas as comunicações criptografadas
- **Autenticação Admin**: Autenticação básica HTTP para painel administrativo

## 📊 Painel Administrativo

Acesse em `http://localhost:8000/api/admin/dashboard` com as credenciais configuradas.

### Endpoints Disponíveis

```
GET    /api/admin/dashboard              - Estatísticas do dashboard
GET    /api/admin/users                  - Listar usuários
POST   /api/admin/users/block            - Bloquear usuário
POST   /api/admin/users/{user_id}/unblock - Desbloquear usuário
GET    /api/admin/logs                   - Visualizar logs
GET    /api/admin/blocked-users          - Listar usuários bloqueados
```

## 🧪 Testes

```bash
# Executar testes
docker-compose exec backend pytest

# Com cobertura
docker-compose exec backend pytest --cov=.
```

## 📝 Logging

Os logs são salvos em `logs/app.log` e incluem:
- Requisições HTTP
- Consultas realizadas
- Erros e exceções
- Ações administrativas

**Nota**: Os logs são anonimizados automaticamente:
- CPF: `XXX.XXX.XXX-XX`
- CNPJ: `XX.XXX.XXX/XXXX-XX`
- Email: `user@example.com`
- Telefone: `(XX)XXXX-XXXX`

## 🔗 APIs Utilizadas

### BrasilAPI
- **URL**: https://brasilapi.com.br
- **Endpoints**: CNPJ, CEP, CPF, Dados Veiculares
- **Autenticação**: Pública
- **Documentação**: https://brasilapi.com.br/docs

### Portal da Transparência
- **URL**: https://api.portaldatransparencia.gov.br
- **Endpoints**: Servidores, Benefícios, Despesas, Licitações
- **Autenticação**: Token (requer cadastro)
- **Documentação**: https://portaldatransparencia.gov.br/api-de-dados

### Have I Been Pwned
- **URL**: https://haveibeenpwned.com/api/v3
- **Endpoints**: Verificação de breaches
- **Autenticação**: API Key
- **Documentação**: https://haveibeenpwned.com/API/v3

## 🐛 Troubleshooting

### Erro de Conexão com PostgreSQL
```bash
# Verificar se o container está rodando
docker-compose ps

# Ver logs do PostgreSQL
docker-compose logs postgres

# Reiniciar o serviço
docker-compose restart postgres
```

### Erro de Rate Limiting
```bash
# Resetar rate limit de um usuário
docker-compose exec backend redis-cli DEL rate_limit:telegram:USER_ID
```

### Webhook não recebendo mensagens
1. Verificar se a URL está correta e acessível publicamente
2. Verificar logs: `docker-compose logs -f backend`
3. Testar webhook manualmente com curl

## 📚 Documentação Adicional

- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Documentação python-telegram-bot](https://python-telegram-bot.readthedocs.io/)
- [Documentação Meta Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api/reference)
- [Documentação SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentação Redis](https://redis.io/documentation)

## 📄 Licença

Este projeto está licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Entre em contato: admin@example.com

## ⚠️ Aviso Legal

Este bot consulta **exclusivamente informações públicas** disponibilizadas por órgãos governamentais brasileiros. O uso indevido para perseguição, discriminação ou violação de privacidade é **proibido**. Os usuários são responsáveis pelo uso das informações consultadas e devem respeitar a Lei Geral de Proteção de Dados (LGPD).

---

**Desenvolvido com ❤️ para transparência e conformidade legal**
