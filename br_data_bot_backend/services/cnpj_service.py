"""
Serviço de consulta CNPJ
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from external_apis import brasil_api
from security import validate_cnpj, hash_user_id, hash_ip_address
from models import QueryLog, QueryType, Platform
from database import SessionLocal

logger = logging.getLogger(__name__)


class CNPJService:
    """Serviço para consulta de dados de CNPJ"""
    
    @staticmethod
    async def consultar_cnpj(
        cnpj: str,
        user_id: str,
        platform: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Consultar dados de CNPJ
        
        Args:
            cnpj: CNPJ a consultar
            user_id: ID do usuário
            platform: Plataforma (telegram ou whatsapp)
            ip_address: IP do usuário
            
        Returns:
            Dicionário com resultado da consulta
        """
        try:
            # Validar CNPJ
            if not validate_cnpj(cnpj):
                logger.warning(f"Invalid CNPJ format: {cnpj}")
                return {
                    "success": False,
                    "error": "CNPJ inválido. Use o formato: XX.XXX.XXX/XXXX-XX ou 14 dígitos"
                }
            
            # Consultar BrasilAPI
            logger.info(f"Consulting CNPJ: {cnpj}")
            data = await brasil_api.get_cnpj(cnpj)
            
            if data is None:
                # Registrar log
                await CNPJService._log_query(
                    user_id=user_id,
                    platform=platform,
                    ip_address=ip_address,
                    status="not_found",
                    error="CNPJ não encontrado"
                )
                
                return {
                    "success": False,
                    "error": "CNPJ não encontrado na base de dados"
                }
            
            # Formatar resposta
            response = {
                "success": True,
                "data": {
                    "razao_social": data.get("razao_social"),
                    "nome_fantasia": data.get("nome_fantasia"),
                    "cnpj": data.get("cnpj"),
                    "situacao_cadastral": data.get("descricao_situacao_cadastral"),
                    "data_inicio_atividade": data.get("data_inicio_atividade"),
                    "natureza_juridica": data.get("natureza_juridica"),
                    "porte": data.get("descricao_porte"),
                    "endereco": {
                        "logradouro": data.get("logradouro"),
                        "numero": data.get("numero"),
                        "complemento": data.get("complemento"),
                        "bairro": data.get("bairro"),
                        "municipio": data.get("municipio"),
                        "uf": data.get("uf"),
                        "cep": data.get("cep")
                    },
                    "contato": {
                        "telefone": data.get("ddd_telefone_1"),
                        "email": data.get("email")
                    },
                    "sócios": data.get("qsa", []),
                    "atividades": {
                        "principal": data.get("cnae_fiscal_descricao"),
                        "secundarias": data.get("cnaes_secundarios", [])
                    }
                }
            }
            
            # Registrar log
            await CNPJService._log_query(
                user_id=user_id,
                platform=platform,
                ip_address=ip_address,
                status="success"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error consulting CNPJ: {e}")
            
            # Registrar log de erro
            await CNPJService._log_query(
                user_id=user_id,
                platform=platform,
                ip_address=ip_address,
                status="error",
                error=str(e)
            )
            
            return {
                "success": False,
                "error": "Erro ao consultar CNPJ. Tente novamente mais tarde."
            }
    
    @staticmethod
    async def _log_query(
        user_id: str,
        platform: str,
        ip_address: str,
        status: str,
        error: Optional[str] = None
    ) -> None:
        """
        Registrar log de consulta
        
        Args:
            user_id: ID do usuário
            platform: Plataforma
            ip_address: IP do usuário
            status: Status da consulta
            error: Mensagem de erro (se houver)
        """
        try:
            db = SessionLocal()
            
            log_entry = QueryLog(
                user_id_hash=hash_user_id(user_id),
                platform=Platform.TELEGRAM if platform == "telegram" else Platform.WHATSAPP,
                query_type=QueryType.CNPJ,
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
cnpj_service = CNPJService()
