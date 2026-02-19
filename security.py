"""
Módulo de segurança: rate limiting, hashing e validações
"""
import hashlib
import logging
import time
from typing import Optional, Tuple
from datetime import datetime, timedelta
import redis
from config import settings

logger = logging.getLogger(__name__)

# Conexão com Redis
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("Redis connected successfully")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Rate limiting will be limited.")
    redis_client = None


def hash_user_id(user_id: str) -> str:
    """
    Gerar hash do ID do usuário para logs anonimizados
    
    Args:
        user_id: ID do usuário
        
    Returns:
        Hash SHA-256 do ID
    """
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]


def hash_ip_address(ip_address: str) -> str:
    """
    Gerar hash do IP para logs anonimizados
    
    Args:
        ip_address: Endereço IP
        
    Returns:
        Hash SHA-256 do IP
    """
    return hashlib.sha256(ip_address.encode()).hexdigest()[:16]


def check_rate_limit(user_id: str, platform: str) -> Tuple[bool, Optional[str]]:
    """
    Verificar se o usuário excedeu o rate limit
    
    Args:
        user_id: ID do usuário
        platform: Plataforma (telegram ou whatsapp)
        
    Returns:
        Tupla (permitido, mensagem_erro)
    """
    if not settings.RATE_LIMIT_ENABLED or redis_client is None:
        return True, None
    
    try:
        key = f"rate_limit:{platform}:{user_id}"
        current_count = redis_client.incr(key)
        
        # Definir expiração na primeira requisição
        if current_count == 1:
            redis_client.expire(key, settings.RATE_LIMIT_PERIOD)
        
        if current_count > settings.RATE_LIMIT_REQUESTS:
            remaining_time = redis_client.ttl(key)
            message = f"Limite de requisições excedido. Tente novamente em {remaining_time} segundos."
            logger.warning(f"Rate limit exceeded for {user_id} on {platform}")
            return False, message
        
        return True, None
        
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        # Permitir em caso de erro
        return True, None


def reset_rate_limit(user_id: str, platform: str) -> None:
    """
    Resetar rate limit de um usuário
    
    Args:
        user_id: ID do usuário
        platform: Plataforma
    """
    if redis_client is None:
        return
    
    try:
        key = f"rate_limit:{platform}:{user_id}"
        redis_client.delete(key)
        logger.info(f"Rate limit reset for {user_id} on {platform}")
    except Exception as e:
        logger.error(f"Failed to reset rate limit: {e}")


def block_user(user_id: str, platform: str, duration_minutes: int = None) -> None:
    """
    Bloquear usuário temporariamente
    
    Args:
        user_id: ID do usuário
        platform: Plataforma
        duration_minutes: Duração do bloqueio em minutos (None = permanente)
    """
    if redis_client is None:
        return
    
    try:
        key = f"blocked_user:{platform}:{user_id}"
        redis_client.set(key, "1")
        
        if duration_minutes:
            redis_client.expire(key, duration_minutes * 60)
        
        logger.warning(f"User {user_id} blocked on {platform}")
    except Exception as e:
        logger.error(f"Failed to block user: {e}")


def is_user_blocked(user_id: str, platform: str) -> bool:
    """
    Verificar se usuário está bloqueado
    
    Args:
        user_id: ID do usuário
        platform: Plataforma
        
    Returns:
        True se bloqueado, False caso contrário
    """
    if redis_client is None:
        return False
    
    try:
        key = f"blocked_user:{platform}:{user_id}"
        return redis_client.exists(key) > 0
    except Exception as e:
        logger.error(f"Failed to check if user is blocked: {e}")
        return False


def unblock_user(user_id: str, platform: str) -> None:
    """
    Desbloquear usuário
    
    Args:
        user_id: ID do usuário
        platform: Plataforma
    """
    if redis_client is None:
        return
    
    try:
        key = f"blocked_user:{platform}:{user_id}"
        redis_client.delete(key)
        logger.info(f"User {user_id} unblocked on {platform}")
    except Exception as e:
        logger.error(f"Failed to unblock user: {e}")


def validate_cnpj(cnpj: str) -> bool:
    """
    Validar formato de CNPJ
    
    Args:
        cnpj: CNPJ a validar
        
    Returns:
        True se válido, False caso contrário
    """
    # Remover caracteres especiais
    cnpj_clean = ''.join(filter(str.isdigit, cnpj))
    
    # Verificar se tem 14 dígitos
    if len(cnpj_clean) != 14:
        return False
    
    # Verificar se não é sequência repetida
    if cnpj_clean == cnpj_clean[0] * 14:
        return False
    
    return True


def validate_cpf(cpf: str) -> bool:
    """
    Validar formato de CPF
    
    Args:
        cpf: CPF a validar
        
    Returns:
        True se válido, False caso contrário
    """
    # Remover caracteres especiais
    cpf_clean = ''.join(filter(str.isdigit, cpf))
    
    # Verificar se tem 11 dígitos
    if len(cpf_clean) != 11:
        return False
    
    # Verificar se não é sequência repetida
    if cpf_clean == cpf_clean[0] * 11:
        return False
    
    return True


def validate_email(email: str) -> bool:
    """
    Validar formato de email
    
    Args:
        email: Email a validar
        
    Returns:
        True se válido, False caso contrário
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
