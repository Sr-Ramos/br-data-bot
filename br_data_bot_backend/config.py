"""
Configurações centralizadas do BR Data Bot
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Aplicação
    APP_NAME: str = "BR Data Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Banco de Dados
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/br_data_bot"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_URL: Optional[str] = os.getenv("TELEGRAM_WEBHOOK_URL")
    TELEGRAM_WEBHOOK_PATH: str = "/webhook/telegram"
    
    # WhatsApp
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    WHATSAPP_API_TOKEN: str = os.getenv("WHATSAPP_API_TOKEN", "")
    WHATSAPP_WEBHOOK_URL: Optional[str] = os.getenv("WHATSAPP_WEBHOOK_URL")
    WHATSAPP_WEBHOOK_PATH: str = "/webhook/whatsapp"
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "br_data_bot_webhook")
    
    # APIs Externas
    BRASIL_API_BASE_URL: str = "https://brasilapi.com.br/api"
    PORTAL_TRANSPARENCIA_BASE_URL: str = "https://api.portaldatransparencia.gov.br"
    PORTAL_TRANSPARENCIA_TOKEN: str = os.getenv("PORTAL_TRANSPARENCIA_TOKEN", "")
    HAVE_I_BEEN_PWNED_API_KEY: Optional[str] = os.getenv("HAVE_I_BEEN_PWNED_API_KEY")
    
    # Segurança
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 10  # Requisições
    RATE_LIMIT_PERIOD: int = 60  # Segundos
    
    # CAPTCHA
    CAPTCHA_ENABLED: bool = True
    RECAPTCHA_SECRET_KEY: Optional[str] = os.getenv("RECAPTCHA_SECRET_KEY")
    RECAPTCHA_SITE_KEY: Optional[str] = os.getenv("RECAPTCHA_SITE_KEY")
    
    # Painel Administrativo
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "your-secret-key-change-in-production")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # Mensagens
    TERMS_OF_USE: str = """
🔒 **AVISO IMPORTANTE - Termos de Uso**

Este bot consulta **exclusivamente informações públicas** disponibilizadas por órgãos governamentais brasileiros.

**Proibições:**
❌ Uso para perseguição, discriminação ou violação de privacidade
❌ Venda ou compartilhamento de dados consultados
❌ Uso para fins ilegais ou fraudulentos
❌ Armazenamento de dados pessoais obtidos

**Responsabilidades:**
✅ Você é responsável pelo uso das informações consultadas
✅ Respeite a privacidade de terceiros
✅ Cumpra com a Lei Geral de Proteção de Dados (LGPD)
✅ Use as informações apenas para fins legítimos

Ao continuar, você concorda com estes termos.
"""

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global de configurações
settings = Settings()
