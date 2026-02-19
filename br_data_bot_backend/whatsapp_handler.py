"""
Handler para processamento de mensagens do WhatsApp
"""
import logging
import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from config import settings
from security import (
    check_rate_limit,
    is_user_blocked,
    validate_cnpj,
    validate_cpf,
    validate_email
)
from services.cnpj_service import cnpj_service
from services.transparencia_service import transparencia_service
from services.veicular_service import veicular_service
from services.breach_service import breach_service
from models import User, Platform
from database import SessionLocal

logger = logging.getLogger(__name__)


class WhatsAppHandler:
    """Handler para processamento de mensagens do WhatsApp"""
    
    @staticmethod
    async def processar_mensagem(
        user_id: str,
        user_name: str,
        message_text: str,
        message_id: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Processar mensagem do WhatsApp
        
        Args:
            user_id: ID do usuário (phone number)
            user_name: Nome do usuário
            message_text: Texto da mensagem
            message_id: ID da mensagem
            ip_address: IP do usuário
            
        Returns:
            Dicionário com resposta a enviar
        """
        try:
            # Verificar se usuário está bloqueado
            if is_user_blocked(user_id, "whatsapp"):
                logger.warning(f"Blocked user attempted to use bot: {user_id}")
                return {
                    "success": False,
                    "message": "❌ Sua conta foi bloqueada. Entre em contato com o administrador.",
                    "send_reply": True
                }
            
            # Verificar rate limit
            allowed, error_message = check_rate_limit(user_id, "whatsapp")
            if not allowed:
                logger.warning(f"Rate limit exceeded for user: {user_id}")
                return {
                    "success": False,
                    "message": f"⏱️ {error_message}",
                    "send_reply": True
                }
            
            # Registrar ou atualizar usuário
            await WhatsAppHandler._upsert_user(user_id, user_name)
            
            # Processar comando ou mensagem
            if message_text.startswith("/"):
                return await WhatsAppHandler._processar_comando(
                    user_id, message_text, ip_address
                )
            
            # Se não for comando, mostrar menu
            return await WhatsAppHandler._mostrar_menu(user_id)
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}")
            return {
                "success": False,
                "message": "❌ Erro ao processar sua mensagem. Tente novamente.",
                "send_reply": True
            }
    
    @staticmethod
    async def _processar_comando(
        user_id: str,
        comando: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """Processar comando do WhatsApp"""
        
        if comando == "/start":
            return await WhatsAppHandler._comando_start(user_id)
        
        elif comando == "/ajuda":
            return await WhatsAppHandler._comando_ajuda()
        
        elif comando == "/consulta_cnpj":
            return {
                "success": True,
                "message": "📋 Digite o CNPJ a consultar (com ou sem formatação):",
                "send_reply": True
            }
        
        elif comando == "/transparencia":
            return {
                "success": True,
                "message": "🔍 Escolha o tipo de consulta:\n\n1️⃣ Servidores públicos\n2️⃣ Benefícios públicos\n\nDigite 1 ou 2:",
                "send_reply": True
            }
        
        elif comando == "/veicular":
            return {
                "success": True,
                "message": "🚗 Digite a placa do veículo (ABC-1234 ou ABC1D34):",
                "send_reply": True
            }
        
        elif comando == "/dados_vazados":
            return {
                "success": True,
                "message": "🔐 Digite seu email para verificar se foi vazado:",
                "send_reply": True
            }
        
        else:
            return await WhatsAppHandler._mostrar_menu(user_id)
    
    @staticmethod
    async def _comando_start(user_id: str) -> Dict[str, Any]:
        """Comando /start"""
        return {
            "success": True,
            "message": settings.TERMS_OF_USE + "\n\n👇 Digite /aceitar para continuar ou /sair para cancelar",
            "send_reply": True
        }
    
    @staticmethod
    async def _comando_ajuda() -> Dict[str, Any]:
        """Comando /ajuda"""
        ajuda = """
🤖 *BR Data Bot - Ajuda*

Este bot consulta dados públicos e legais no Brasil.

*Comandos disponíveis:*

/start - Iniciar o bot
/ajuda - Mostrar esta mensagem
/consulta_cnpj - Consultar dados de empresa (CNPJ)
/transparencia - Consultar dados públicos (Portal da Transparência)
/veicular - Consultar dados de veículos
/dados_vazados - Verificar se email foi vazado
/menu - Mostrar menu principal

*Informações importantes:*

✅ Todos os dados consultados são públicos e oficiais
✅ Não armazenamos dados pessoais sensíveis
✅ Respeite a privacidade de terceiros
✅ Use as informações apenas para fins legítimos

*Dúvidas?*

Entre em contato com o administrador através do email: admin@example.com
"""
        return {
            "success": True,
            "message": ajuda,
            "send_reply": True
        }
    
    @staticmethod
    async def _mostrar_menu(user_id: str) -> Dict[str, Any]:
        """Mostrar menu principal"""
        menu = """
📱 *Menu Principal*

Escolha uma opção:

1️⃣ Consultar CNPJ
2️⃣ Portal da Transparência
3️⃣ Dados Veiculares
4️⃣ Verificar Dados Vazados
5️⃣ Ajuda

Digite o número ou use os comandos:
/consulta_cnpj
/transparencia
/veicular
/dados_vazados
/ajuda
"""
        return {
            "success": True,
            "message": menu,
            "send_reply": True
        }
    
    @staticmethod
    async def processar_entrada_cnpj(
        user_id: str,
        cnpj: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """Processar entrada de CNPJ"""
        
        resultado = await cnpj_service.consultar_cnpj(
            cnpj=cnpj,
            user_id=user_id,
            platform="whatsapp",
            ip_address=ip_address
        )
        
        if resultado["success"]:
            data = resultado["data"]
            mensagem = f"""
📊 *Resultado da Consulta CNPJ*

*Razão Social:* {data.get('razao_social')}
*Nome Fantasia:* {data.get('nome_fantasia')}
*CNPJ:* {data.get('cnpj')}
*Situação:* {data.get('situacao_cadastral')}
*Data de Início:* {data.get('data_inicio_atividade')}
*Natureza Jurídica:* {data.get('natureza_juridica')}
*Porte:* {data.get('porte')}

*Endereço:*
{data.get('endereco', {}).get('logradouro')} {data.get('endereco', {}).get('numero')}
{data.get('endereco', {}).get('bairro')} - {data.get('endereco', {}).get('municipio')}/{data.get('endereco', {}).get('uf')}
CEP: {data.get('endereco', {}).get('cep')}

*Contato:*
Telefone: {data.get('contato', {}).get('telefone')}
Email: {data.get('contato', {}).get('email')}
"""
        else:
            mensagem = f"❌ {resultado['error']}"
        
        return {
            "success": resultado["success"],
            "message": mensagem,
            "send_reply": True
        }
    
    @staticmethod
    async def processar_entrada_email(
        user_id: str,
        email: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """Processar entrada de email para verificação de vazamento"""
        
        resultado = await breach_service.consultar_email_vazado(
            email=email,
            user_id=user_id,
            platform="whatsapp",
            ip_address=ip_address
        )
        
        if resultado["success"]:
            data = resultado["data"]
            
            if resultado["status"] == "safe":
                mensagem = f"""
✅ *Verificação de Dados Vazados*

{resultado['message']}

Email: {email}
Vazamentos encontrados: 0

{data.get('recommendation')}
"""
            else:
                breaches_info = ""
                for breach in data.get("breaches", []):
                    breaches_info += f"\n• {breach['name']} ({breach['date']})"
                
                mensagem = f"""
⚠️ *Verificação de Dados Vazados*

{resultado['message']}

Email: {email}
Vazamentos encontrados: {data.get('breach_count')}

{breaches_info}

{data.get('recommendation')}
"""
        else:
            mensagem = f"❌ {resultado['error']}"
        
        return {
            "success": resultado["success"],
            "message": mensagem,
            "send_reply": True
        }
    
    @staticmethod
    async def enviar_mensagem(
        phone_number: str,
        message_text: str
    ) -> bool:
        """
        Enviar mensagem via WhatsApp Cloud API
        
        Args:
            phone_number: Número de telefone do destinatário
            message_text: Texto da mensagem
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            url = f"https://graph.instagram.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
            
            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message_text
                }
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    logger.info(f"Message sent to {phone_number}")
                    return True
                else:
                    logger.error(f"Failed to send message: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    @staticmethod
    async def _upsert_user(
        user_id: str,
        user_name: Optional[str]
    ) -> None:
        """Registrar ou atualizar usuário"""
        try:
            db = SessionLocal()
            
            user = db.query(User).filter(
                User.user_id == user_id,
                User.platform == Platform.WHATSAPP
            ).first()
            
            if user:
                user.first_name = user_name
                user.last_interaction = datetime.utcnow()
            else:
                user = User(
                    user_id=user_id,
                    platform=Platform.WHATSAPP,
                    first_name=user_name,
                    phone_number=user_id,
                    accepted_terms=False
                )
                db.add(user)
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Error upserting user: {e}")


# Instância global do handler
whatsapp_handler = WhatsAppHandler()
