"""
Modelos de dados para o BR Data Bot
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class QueryType(str, enum.Enum):
    """Tipos de consultas realizadas"""
    CNPJ = "cnpj"
    CPF = "cpf"
    TRANSPARENCIA = "transparencia"
    VEICULAR = "veicular"
    DADOS_VAZADOS = "dados_vazados"


class Platform(str, enum.Enum):
    """Plataformas de acesso"""
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"


class User(Base):
    """Modelo de usuário do bot"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, nullable=False)  # ID do Telegram ou WhatsApp
    platform = Column(Enum(Platform), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    username = Column(String(255))
    phone_number = Column(String(20))
    accepted_terms = Column(Boolean, default=False)
    blocked = Column(Boolean, default=False)
    block_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    """Log de consultas realizadas (anonimizado)"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True)
    user_id_hash = Column(String(255), nullable=False)  # Hash do ID do usuário
    platform = Column(Enum(Platform), nullable=False)
    query_type = Column(Enum(QueryType), nullable=False)
    query_input = Column(String(255))  # Entrada da consulta (anonimizada)
    result_status = Column(String(50))  # success, error, rate_limited, etc
    error_message = Column(Text)
    response_time_ms = Column(Integer)
    ip_address_hash = Column(String(255))  # Hash do IP
    created_at = Column(DateTime, default=datetime.utcnow)


class RateLimit(Base):
    """Controle de rate limiting"""
    __tablename__ = "rate_limits"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, unique=True)
    platform = Column(Enum(Platform), nullable=False)
    request_count = Column(Integer, default=0)
    last_reset = Column(DateTime, default=datetime.utcnow)
    blocked_until = Column(DateTime)


class AdminLog(Base):
    """Log de ações administrativas"""
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True)
    admin_username = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    target_user_id = Column(String(255))
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class BlockedUser(Base):
    """Usuários bloqueados"""
    __tablename__ = "blocked_users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    reason = Column(Text, nullable=False)
    blocked_at = Column(DateTime, default=datetime.utcnow)
    blocked_by = Column(String(255))  # Admin que bloqueou
    unblock_at = Column(DateTime)  # Quando será desbloqueado (None = permanente)
