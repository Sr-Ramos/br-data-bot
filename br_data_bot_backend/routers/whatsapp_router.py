"""Router para webhook do WhatsApp"""
import logging
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import Optional, List
from config import settings
from whatsapp_handler import whatsapp_handler

logger = logging.getLogger(__name__)
router = APIRouter()


class WhatsAppMessage(BaseModel):
    """Modelo de mensagem do WhatsApp"""
    from_: str
    id: str
    timestamp: str
    text: Optional[dict] = None
    type: str


class WhatsAppContact(BaseModel):
    """Modelo de contato do WhatsApp"""
    profile: dict
    wa_id: str


class WhatsAppMetadata(BaseModel):
    """Metadados da mensagem do WhatsApp"""
    display_phone_number: str
    phone_number_id: str


class WhatsAppValue(BaseModel):
    """Valor da mensagem do WhatsApp"""
    messaging_product: str
    metadata: WhatsAppMetadata
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessage]] = None


class WhatsAppEntry(BaseModel):
    """Entrada do webhook do WhatsApp"""
    id: str
    changes: List[dict]


class WhatsAppWebhook(BaseModel):
    """Modelo de webhook do WhatsApp"""
    object: str
    entry: List[WhatsAppEntry]


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(webhook: WhatsAppWebhook, request: Request):
    """
    Webhook para receber mensagens do WhatsApp
    
    Args:
        webhook: Dados do webhook do WhatsApp
        request: Requisição HTTP
        
    Returns:
        Confirmação de recebimento
    """
    try:
        logger.info(f"Received WhatsApp webhook: {webhook.object}")
        
        # Obter IP do cliente
        ip_address = request.client.host if request.client else "unknown"
        
        for entry in webhook.entry:
            for change in entry.changes:
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    
                    # Obter contatos
                    contacts = value.get("contacts", [])
                    contact_map = {c.get("wa_id"): c.get("profile", {}).get("name") for c in contacts}
                    
                    # Processar mensagens
                    messages = value.get("messages", [])
                    for message in messages:
                        user_id = message.get("from")
                        message_id = message.get("id")
                        message_type = message.get("type")
                        user_name = contact_map.get(user_id, "User")
                        
                        logger.info(f"Message from {user_id}: type={message_type}")
                        
                        # Processar diferentes tipos de mensagens
                        if message_type == "text":
                            text_content = message.get("text", {}).get("body", "")
                            logger.info(f"Text message: {text_content}")
                            
                            # Processar com handler
                            resultado = await whatsapp_handler.processar_mensagem(
                                user_id=user_id,
                                user_name=user_name,
                                message_text=text_content,
                                message_id=message_id,
                                ip_address=ip_address
                            )
                            
                            # Enviar resposta
                            if resultado.get("send_reply"):
                                await whatsapp_handler.enviar_mensagem(
                                    phone_number=user_id,
                                    message_text=resultado.get("message", "")
                                )
                        
                        elif message_type == "interactive":
                            interactive = message.get("interactive", {})
                            logger.info(f"Interactive message: {interactive}")
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")


@router.get("/webhook/whatsapp")
async def whatsapp_webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Verificação de webhook do WhatsApp
    
    Args:
        hub_mode: Modo do hub
        hub_verify_token: Token de verificação
        hub_challenge: Desafio de verificação
        
    Returns:
        Desafio se verificado com sucesso
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified")
        return int(hub_challenge)
    else:
        logger.warning("WhatsApp webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")
