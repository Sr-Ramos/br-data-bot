"""
Serviço de consulta de dados vazados na internet
"""
import logging
from typing import Optional, Dict, Any
from external_apis import data_breach
from security import validate_email, hash_user_id, hash_ip_address
from models import QueryLog, QueryType, Platform
from database import SessionLocal

logger = logging.getLogger(__name__)


class BreachService:
    """Serviço para consulta de dados vazados"""
    
    @staticmethod
    async def consultar_email_vazado(
        email: str,
        user_id: str,
        platform: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Verificar se email foi vazado na internet
        
        Args:
            email: Email a verificar
            user_id: ID do usuário
            platform: Plataforma
            ip_address: IP do usuário
            
        Returns:
            Dicionário com resultado da consulta
        """
        try:
            # Validar email
            if not validate_email(email):
                logger.warning(f"Invalid email format: {email}")
                return {
                    "success": False,
                    "error": "Email inválido. Verifique o formato e tente novamente."
                }
            
            # Consultar Have I Been Pwned
            logger.info(f"Checking if email was breached: {email}")
            data = await data_breach.check_email_breach(email)
            
            if data is None:
                await BreachService._log_query(
                    user_id=user_id,
                    platform=platform,
                    ip_address=ip_address,
                    status="error",
                    error="API de dados vazados não disponível"
                )
                
                return {
                    "success": False,
                    "error": "Serviço de verificação temporariamente indisponível. Tente novamente mais tarde."
                }
            
            # Formatar resposta
            if data["status"] == "safe":
                response = {
                    "success": True,
                    "status": "safe",
                    "message": "✅ Boas notícias! Este email não foi encontrado em vazamentos conhecidos.",
                    "data": {
                        "email": email,
                        "breaches": [],
                        "recommendation": "Mantenha seus dados seguros usando senhas fortes e autenticação de dois fatores."
                    }
                }
            else:
                # Email foi encontrado em vazamentos
                breaches = data.get("breaches", [])
                response = {
                    "success": True,
                    "status": "compromised",
                    "message": f"⚠️ Este email foi encontrado em {len(breaches)} vazamento(s) de dados.",
                    "data": {
                        "email": email,
                        "breach_count": len(breaches),
                        "breaches": [
                            {
                                "name": breach.get("Name"),
                                "title": breach.get("Title"),
                                "date": breach.get("BreachDate"),
                                "data_classes": breach.get("DataClasses", []),
                                "is_verified": breach.get("IsVerified"),
                                "is_sensitive": breach.get("IsSensitive"),
                                "is_retired": breach.get("IsRetired"),
                                "is_spam_list": breach.get("IsSpamList"),
                                "logo_path": breach.get("LogoPath")
                            }
                            for breach in breaches
                        ],
                        "recommendation": "Recomendamos: 1) Alterar senha imediatamente; 2) Ativar autenticação de dois fatores; 3) Monitorar atividades suspeitas na conta."
                    }
                }
            
            # Registrar log
            await BreachService._log_query(
                user_id=user_id,
                platform=platform,
                ip_address=ip_address,
                status="success"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error checking email breach: {e}")
            
            await BreachService._log_query(
                user_id=user_id,
                platform=platform,
                ip_address=ip_address,
                status="error",
                error=str(e)
            )
            
            return {
                "success": False,
                "error": "Erro ao verificar dados vazados. Tente novamente mais tarde."
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
                query_type=QueryType.DADOS_VAZADOS,
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
breach_service = BreachService()
