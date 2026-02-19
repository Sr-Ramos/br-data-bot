"""
Router para health checks e status da aplicação
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Verificar saúde da aplicação"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "br-data-bot"
    }


@router.get("/status")
async def status():
    """Obter status da aplicação"""
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "br-data-bot"
    }
