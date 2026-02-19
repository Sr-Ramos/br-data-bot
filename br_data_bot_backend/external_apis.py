"""
Módulo para integração com APIs externas brasileiras
"""
import logging
import httpx
import asyncio
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


class BrasilAPIClient:
    """Cliente para BrasilAPI"""
    
    def __init__(self):
        self.base_url = settings.BRASIL_API_BASE_URL
        self.timeout = 10
    
    async def get_cnpj(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Consultar dados de CNPJ via BrasilAPI
        
        Args:
            cnpj: CNPJ a consultar (com ou sem formatação)
            
        Returns:
            Dicionário com dados da empresa ou None
        """
        try:
            # Remover formatação
            cnpj_clean = ''.join(filter(str.isdigit, cnpj))
            
            url = f"{self.base_url}/cnpj/v1/{cnpj_clean}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"CNPJ {cnpj_clean} consulted successfully")
                    return data
                elif response.status_code == 404:
                    logger.warning(f"CNPJ {cnpj_clean} not found")
                    return None
                else:
                    logger.error(f"BrasilAPI error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get CNPJ data: {e}")
            return None
    
    async def get_cep(self, cep: str) -> Optional[Dict[str, Any]]:
        """
        Consultar dados de CEP via BrasilAPI
        
        Args:
            cep: CEP a consultar
            
        Returns:
            Dicionário com dados do endereço ou None
        """
        try:
            cep_clean = ''.join(filter(str.isdigit, cep))
            
            url = f"{self.base_url}/address/v2/{cep_clean}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"CEP {cep_clean} consulted successfully")
                    return data
                else:
                    logger.warning(f"CEP {cep_clean} not found")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get CEP data: {e}")
            return None


class PortalTransparenciaClient:
    """Cliente para API do Portal da Transparência"""
    
    def __init__(self):
        self.base_url = settings.PORTAL_TRANSPARENCIA_BASE_URL
        self.token = settings.PORTAL_TRANSPARENCIA_TOKEN
        self.timeout = 10
    
    async def get_servidores_por_cpf(self, cpf: str) -> Optional[Dict[str, Any]]:
        """
        Consultar dados de servidores públicos por CPF
        
        Args:
            cpf: CPF a consultar
            
        Returns:
            Dicionário com dados dos servidores ou None
        """
        if not self.token:
            logger.warning("Portal da Transparência token not configured")
            return None
        
        try:
            cpf_clean = ''.join(filter(str.isdigit, cpf))
            
            url = f"{self.base_url}/api-de-dados/servidores"
            params = {
                "cpf": cpf_clean,
                "token": self.token
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Servidor data for CPF {cpf_clean} retrieved")
                    return data
                else:
                    logger.warning(f"No servidor data found for CPF {cpf_clean}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get servidor data: {e}")
            return None
    
    async def get_beneficios_por_cpf(self, cpf: str) -> Optional[Dict[str, Any]]:
        """
        Consultar benefícios por CPF (Bolsa Família, Auxílio, etc)
        
        Args:
            cpf: CPF a consultar
            
        Returns:
            Dicionário com dados dos benefícios ou None
        """
        if not self.token:
            logger.warning("Portal da Transparência token not configured")
            return None
        
        try:
            cpf_clean = ''.join(filter(str.isdigit, cpf))
            
            # Tentar múltiplos endpoints de benefícios
            endpoints = [
                f"{self.base_url}/api-de-dados/bolsa-familia-disponivel-por-cpf-ou-nis",
                f"{self.base_url}/api-de-dados/auxilio-brasil-sacado-por-nis",
                f"{self.base_url}/api-de-dados/bpc-por-cpf-ou-nis"
            ]
            
            results = {}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for endpoint in endpoints:
                    try:
                        params = {
                            "cpfOuNis": cpf_clean,
                            "token": self.token
                        }
                        
                        response = await client.get(endpoint, params=params)
                        
                        if response.status_code == 200:
                            data = response.json()
                            endpoint_name = endpoint.split("/")[-1]
                            results[endpoint_name] = data
                            
                    except Exception as e:
                        logger.warning(f"Failed to query {endpoint}: {e}")
                        continue
            
            if results:
                logger.info(f"Benefícios data for CPF {cpf_clean} retrieved")
                return results
            else:
                logger.warning(f"No benefícios data found for CPF {cpf_clean}")
                return None
                    
        except Exception as e:
            logger.error(f"Failed to get benefícios data: {e}")
            return None


class DataBreachClient:
    """Cliente para consulta de dados vazados"""
    
    def __init__(self):
        self.timeout = 10
    
    async def check_email_breach(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Verificar se email foi vazado (usando Have I Been Pwned)
        
        Args:
            email: Email a verificar
            
        Returns:
            Dicionário com informações de vazamento ou None
        """
        if not settings.HAVE_I_BEEN_PWNED_API_KEY:
            logger.warning("Have I Been Pwned API key not configured")
            return None
        
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            
            headers = {
                "User-Agent": "BR-Data-Bot/1.0",
                "Authorization": f"Bearer {settings.HAVE_I_BEEN_PWNED_API_KEY}"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Email {email} found in {len(data)} breaches")
                    return {
                        "email": email,
                        "breaches": data,
                        "status": "found"
                    }
                elif response.status_code == 404:
                    logger.info(f"Email {email} not found in breaches")
                    return {
                        "email": email,
                        "breaches": [],
                        "status": "safe"
                    }
                else:
                    logger.warning(f"Have I Been Pwned API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to check email breach: {e}")
            return None


# Instâncias globais dos clientes
brasil_api = BrasilAPIClient()
portal_transparencia = PortalTransparenciaClient()
data_breach = DataBreachClient()
