# Guia de Instalação - BR Data Bot

Este documento fornece instruções detalhadas para instalar e configurar o BR Data Bot.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

- **Sistema Operacional**: Linux (Ubuntu 20.04+), macOS ou Windows com WSL2
- **Docker**: Versão 20.10+
- **Docker Compose**: Versão 1.29+
- **Git**: Para clonar o repositório
- **Tokens de API**: Telegram, WhatsApp, etc.

## 🐳 Instalação com Docker (Recomendado)

### 1. Verificar Instalação do Docker

```bash
docker --version
docker-compose --version
```

Se não tiver Docker instalado, siga as instruções em https://docs.docker.com/get-docker/

### 2. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/br_data_bot.git
cd br_data_bot_backend
```

### 3. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```bash
nano .env
```

Configurações essenciais:

```env
# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui

# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id
WHATSAPP_API_TOKEN=seu_token_aqui
WHATSAPP_WEBHOOK_VERIFY_TOKEN=seu_token_verificacao

# Banco de Dados
DB_PASSWORD=senha_segura_aqui

# Admin
ADMIN_PASSWORD=senha_admin_segura
ADMIN_SECRET_KEY=chave_secreta_muito_segura
```

### 4. Iniciar Serviços

```bash
# Construir imagens (primeira vez)
docker-compose build

# Iniciar serviços em background
docker-compose up -d

# Verificar status
docker-compose ps
```

### 5. Verificar Logs

```bash
# Ver logs em tempo real
docker-compose logs -f backend

# Ver logs de um serviço específico
docker-compose logs postgres
docker-compose logs redis
```

### 6. Testar Aplicação

```bash
# Health check
curl http://localhost:8000/api/health

# Resposta esperada:
# {"status":"healthy","timestamp":"2024-01-15T10:30:00","service":"br-data-bot"}
```

## 🐍 Instalação Local (Sem Docker)

### 1. Instalar Python 3.11

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

**macOS:**
```bash
brew install python@3.11
```

**Windows:**
Baixe em https://www.python.org/downloads/

### 2. Criar Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

Criar banco de dados:

```bash
sudo -u postgres psql

CREATE USER br_data_bot WITH PASSWORD 'senha_segura';
CREATE DATABASE br_data_bot OWNER br_data_bot;
GRANT ALL PRIVILEGES ON DATABASE br_data_bot TO br_data_bot;
\q
```

### 5. Configurar Redis

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

### 6. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
nano .env
```

Ajuste para sua instalação local:

```env
DATABASE_URL=postgresql://br_data_bot:senha_segura@localhost:5432/br_data_bot
REDIS_URL=redis://localhost:6379/0
```

### 7. Inicializar Banco de Dados

```bash
python -c "from database import init_db; init_db()"
```

### 8. Iniciar Aplicação

```bash
python main.py
```

A aplicação estará disponível em `http://localhost:8000`

## 🔧 Configuração Avançada

### Variáveis de Ambiente Importantes

As seguintes variáveis de ambiente podem ser configuradas no arquivo `.env`:

**DEBUG** - Ativa modo debug (deve ser False em produção)
**HOST** - Host da aplicação (padrão: 0.0.0.0)
**PORT** - Porta da aplicação (padrão: 8000)
**DATABASE_URL** - URL de conexão do PostgreSQL
**REDIS_URL** - URL de conexão do Redis
**TELEGRAM_BOT_TOKEN** - Token do bot Telegram
**WHATSAPP_API_TOKEN** - Token da API WhatsApp
**RATE_LIMIT_REQUESTS** - Número máximo de requisições (padrão: 10)
**RATE_LIMIT_PERIOD** - Período em segundos (padrão: 60)
**LOG_LEVEL** - Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
**LOG_FILE** - Caminho do arquivo de log

### Rate Limiting

Configure o rate limiting em `.env`:

```env
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=10      # 10 requisições
RATE_LIMIT_PERIOD=60        # por 60 segundos
```

### Logging

Configure o nível de log:

```env
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/app.log
```

## 🧪 Testes

### Executar Testes

```bash
# Com Docker
docker-compose exec backend pytest

# Localmente
pytest
```

### Testes com Cobertura

```bash
# Com Docker
docker-compose exec backend pytest --cov=. --cov-report=html

# Localmente
pytest --cov=. --cov-report=html
```

Abra `htmlcov/index.html` no navegador para ver o relatório.

## 🔍 Troubleshooting

### Erro: "Port 5432 is already in use"

```bash
# Encontrar processo usando a porta
lsof -i :5432

# Ou com Docker
docker-compose down
```

### Erro: "Cannot connect to PostgreSQL"

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Ou com Docker
docker-compose logs postgres
```

### Erro: "ModuleNotFoundError"

```bash
# Reinstalar dependências
pip install -r requirements.txt

# Ou com Docker
docker-compose build --no-cache
```

### Erro: "Redis connection refused"

```bash
# Verificar se Redis está rodando
redis-cli ping

# Ou com Docker
docker-compose logs redis
```

## 📚 Próximos Passos

1. Leia [README.md](README.md) para documentação completa
2. Configure os webhooks (veja [DEPLOY.md](DEPLOY.md))
3. Teste os comandos do bot
4. Configure o painel administrativo

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `docker-compose logs` ou `tail -f logs/app.log`
2. Consulte a documentação: [README.md](README.md)
3. Abra uma issue no GitHub
4. Entre em contato: admin@example.com

---

**Instalação concluída com sucesso! 🎉**
