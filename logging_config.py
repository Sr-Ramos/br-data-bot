"""
Configuração de logging anonimizado
"""
import logging
import logging.handlers
import os
from config import settings

# Criar diretório de logs se não existir
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)


class AnonymizedFormatter(logging.Formatter):
    """Formatter que anonimiza dados sensíveis nos logs"""
    
    def format(self, record):
        # Anonimizar CPF (XXX.XXX.XXX-XX)
        import re
        record.msg = re.sub(
            r'\d{3}\.\d{3}\.\d{3}-\d{2}',
            'XXX.XXX.XXX-XX',
            str(record.msg)
        )
        
        # Anonimizar CNPJ (XX.XXX.XXX/XXXX-XX)
        record.msg = re.sub(
            r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',
            'XX.XXX.XXX/XXXX-XX',
            str(record.msg)
        )
        
        # Anonimizar email
        record.msg = re.sub(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'user@example.com',
            str(record.msg)
        )
        
        # Anonimizar telefone
        record.msg = re.sub(
            r'\(\d{2}\)\s?\d{4,5}-\d{4}',
            '(XX)XXXX-XXXX',
            str(record.msg)
        )
        
        return super().format(record)


def setup_logging():
    """Configurar logging da aplicação"""
    
    # Obter logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Handler para arquivo
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Formatter anonimizado
    formatter = AnonymizedFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Adicionar handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger


# Configurar logging ao importar o módulo
logger = setup_logging()
