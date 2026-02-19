"""
Serviço de consulta de dados veiculares
"""
import logging
from typing import Optional, Dict, Any
from security import hash_user_id, hash_ip_address
from models import QueryLog, QueryType, Platform
from database import SessionLocal

logger = logging.getLogger(__name__)


class VeicularService:
    """Serviço para consulta de dados veiculares"""
    
    @staticmethod
    async def consultar_veiculo(
        placa: str,
        user_id: str,
        platform: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Consultar dados de veículo (redirecionamento para sistemas oficiais)
        
        Args:
            placa: Placa do veículo
            user_id: ID do usuário
            platform: Plataforma
            ip_address: IP do usuário
            
        Returns:
            Dicionário com informações de redirecionamento
        """
        try:
            # Validar formato de placa
            placa_clean = placa.replace("-", "").replace(" ", "").upper()
            
            if len(placa_clean) != 7:
                logger.warning(f"Invalid plate format: {placa}")
                return {
                    "success": False,
                    "error": "Placa inválida. Use o formato: ABC-1234 ou ABC1D34"
                }
            
            logger.info(f"Redirecting to vehicle check for plate: {placa_clean}")
            
            # Registrar log
            await VeicularService._log_query(
                user_id=user_id,
                platform=platform,
                ip_address=ip_address,
                status="redirected"
            )
            
            # Retornar informações de redirecionamento
            return {
                "success": True,
                "message": "Redirecionando para sistemas oficiais de consulta veicular",
                "options": [
                    {
                        "name": "SINESP (Segurança Pública)",
                        "url": "https://www.sinesp.gov.br/sinesp-cidadao/",
                        "description": "Consulta de informações de segurança pública"
                    },
                    {
                        "name": "Detran (Trânsito)",
                        "url": "https://www.detran.sp.gov.br/",
                        "description": "Informações de trânsito e multas (varia por estado)"
                    },
                    {
                        "name": "CDT (Central de Dados de Trânsito)",
                        "url": "https://www.cdt.org.br/",
                        "description": "Dados de trânsito e veículos"
                    }
                ],
                "aviso": "⚠️ Consultas de dados veiculares devem ser feitas através de sistemas oficiais. Não armazenamos dados sensíveis."
            }
            
        except Exception as e:
            logger.error(f"Error processing vehicle query: {e}")
            
            await VeicularService._log_query(
                user_id=user_id,
                platform=platform,
                ip_address=ip_address,
                status="error",
                error=str(e)
            )
            
            return {
                "success": False,
                "error": "Erro ao processar consulta. Tente novamente mais tarde."
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
                query_type=QueryType.VEICULAR,
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
veicular_service = VeicularService()
