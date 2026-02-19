"""
Serviço de consulta Portal da Transparência
"""
import logging
from typing import Optional, Dict, Any
from external_apis import portal_transparencia
from security import validate_cpf, validate_cnpj, hash_user_id, hash_ip_address
from models import QueryLog, QueryType, Platform
from database import SessionLocal

logger = logging.getLogger(__name__)


class TransparenciaService:
    """Serviço para consulta de dados públicos no Portal da Transparência"""
    
    @staticmethod
    async def consultar_servidores_por_cpf(
        cpf: str,
        user_id: str,
        platform: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Consultar dados de servidores públicos por CPF
        
        Args:
            cpf: CPF a consultar
            user_id: ID do usuário
            platform: Plataforma
            ip_address: IP do usuário
            
        Returns:
            Dicionário com resultado da consulta
        """
        try:
            # Validar CPF
            if not validate_cpf(cpf):
                logger.warning(f"Invalid CPF format: {cpf}")
                return {
                    "success": False,
                    "error": "CPF inválido. Use o formato: XXX.XXX.XXX-XX ou 11 dígitos"
                }
            
            # Consultar Portal da Transparência
            logger.info(f"Consulting servidor data for CPF: {cpf}")
            data = await portal_transparencia.get_servidores_por_cpf(cpf)
            
            if data is None:
                await TransparenciaService._log_query(
                    user_id=user_id,
                    platform=platform,
                    ip_address=ip_address,
                    status="not_found",
                    error="CPF não encontrado"
                )
                
                return {
                    "success": False,
                    "error": "Nenhum servidor público encontrado com este CPF"
                }
            
            # Formatar resposta
            response = {
                "success": True,
                "data": data,
                "aviso": "Estes são dados públicos disponibilizados pelo Portal da Transparência"
            }
            
            # Registrar log
            await TransparenciaService._log_query(
                user_id=user_id,
                platform=platform,
                ip_address=ip_address,
                status="success"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error consulting servidor data: {e}")
            
            await TransparenciaService._log_query(
                user_id=user_id,
                platform=platform,
                ip_address=ip_address,
                status="error",
                error=str(e)
            )
            
            return {
                "success": False,
                "error": "Erro ao consultar dados. Tente novamente mais tarde."
            }
    
    @staticmethod
    async def consultar_beneficios_por_cpf(
        cpf: str,
        user_id: str,
        platform: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Consultar benefícios públicos por CPF
        
        Args:
            cpf: CPF a consultar
            user_id: ID do usuário
            platform: Plataforma
            ip_address: IP do usuário
            
        Returns:
            Dicionário com resultado da consulta
        """
        try:
            # Validar CPF
            if not validate_cpf(cpf):
                logger.warning(f"Invalid CPF format: {cpf}")
                return {
                    "success": False,
                    "error": "CPF inválido. Use o formato: XXX.XXX.XXX-XX ou 11 dígitos"
                }
            
            # Consultar Portal da Transparência
            logger.info(f"Consulting benefícios for CPF: {cpf}")
            data = await portal_transparencia.get_beneficios_por_cpf(cpf)
            
            if data is None or len(data) == 0:
                await TransparenciaService._log_query(
                    user_id=user_id,
                    platform=platform,
                    ip_address=ip_address,
                    status="not_found",
                    error="Nenhum benefício encontrado"
                )
                
                return {
                    "success": False,
                    "error": "Nenhum benefício público encontrado para este CPF"
                }
            
            # Formatar resposta
            response = {
                "success": True,
                "data": data,
                "aviso": "Estes são dados públicos disponibilizados pelo Portal da Transparência"
            }
            
            # Registrar log
            await TransparenciaService._log_query(
                user_id=user_id,
                platform=platform,
                ip_address=ip_address,
                status="success"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error consulting benefícios: {e}")
            
            await TransparenciaService._log_query(
                user_id=user_id,
                platform=platform,
                ip_address=ip_address,
                status="error",
                error=str(e)
            )
            
            return {
                "success": False,
                "error": "Erro ao consultar benefícios. Tente novamente mais tarde."
            }
    
    @staticmethod
    async def _log_query(
        user_id: str,
        platform: str,
        ip_address: str,
        status: str,
        error: Optional[str] = None
    ) -> None:
        """Registrar log de consulta"""
        try:
            db = SessionLocal()
            
            log_entry = QueryLog(
                user_id_hash=hash_user_id(user_id),
                platform=Platform.TELEGRAM if platform == "telegram" else Platform.WHATSAPP,
                query_type=QueryType.TRANSPARENCIA,
                result_status=status,
                error_message=error,
                ip_address_hash=hash_ip_address(ip_address)
            )
            
            db.add(log_entry)
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Error logging query: {e}")


# Instância global do serviço
transparencia_service = TransparenciaService()
