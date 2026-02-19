"""Router para webhook do Telegram"""
import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from telegram_handler import telegram_handler

logger = logging.getLogger(__name__)
router = APIRouter()


class TelegramUpdate(BaseModel):
    """Modelo de atualização do Telegram"""
    update_id: int
    message: Optional[dict] = None
    callback_query: Optional[dict] = None


@router.post("/webhook/telegram")
async def telegram_webhook(update: TelegramUpdate, request: Request):
    """
    Webhook para receber atualizações do Telegram
    
    Args:
        update: Atualização do Telegram
        request: Requisição HTTP
        
    Returns:
        Confirmação de recebimento
    """
    try:
        logger.info(f"Received Telegram update: {update.update_id}")
        
        # Obter IP do cliente
        ip_address = request.client.host if request.client else "unknown"
        
        # Processar mensagem
        if update.message:
            message = update.message
            user_id = str(message.get("from", {}).get("id"))
            text = message.get("text", "")
            username = message.get("from", {}).get("username", "")
            first_name = message.get("from", {}).get("first_name", "")
            
            logger.info(f"Message from {user_id}: {text}")
            
            # Processar com handler
            resultado = await telegram_handler.processar_mensagem(
                user_id=user_id,
                username=username,
                first_name=first_name,
                text=text,
                ip_address=ip_address
            )
            
            logger.info(f"Response for {user_id}: {resultado.get('message', '')[:50]}...")
        
        # Processar callback query
        if update.callback_query:
            callback = update.callback_query
            user_id = str(callback.get("from", {}).get("id"))
            data = callback.get("data", "")
            
            logger.info(f"Callback from {user_id}: {data}")
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Error processing Telegram update: {e}")
        raise HTTPException(status_code=500, detail="Error processing update")


@router.get("/webhook/telegram")
async def telegram_webhook_get():
    """
    GET endpoint para webhook do Telegram (para testes)
    """
    return {"message": "Telegram webhook is active"}
