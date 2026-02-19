# Contribuindo para BR Data Bot

Obrigado por seu interesse em contribuir! Este documento fornece diretrizes para contribuições.

## Como Contribuir

### 1. Fork o Repositório

```bash
git clone https://github.com/seu-usuario/br_data_bot.git
cd br_data_bot_backend
```

### 2. Criar uma Branch

```bash
git checkout -b feature/sua-feature
```

### 3. Fazer Mudanças

- Siga o estilo de código existente
- Adicione testes para novas funcionalidades
- Atualize documentação conforme necessário

### 4. Commit e Push

```bash
git add .
git commit -m "Descrição clara da mudança"
git push origin feature/sua-feature
```

### 5. Abrir Pull Request

- Descreva as mudanças claramente
- Referencie issues relacionadas
- Aguarde revisão

## Diretrizes de Código

### Python

- Siga PEP 8
- Use type hints
- Documente funções públicas
- Mantenha linhas com máximo 100 caracteres

### Exemplo

```python
def consultar_cnpj(cnpj: str, user_id: str) -> Dict[str, Any]:
    """
    Consultar dados de CNPJ.
    
    Args:
        cnpj: CNPJ a consultar
        user_id: ID do usuário
        
    Returns:
        Dicionário com dados da empresa
    """
    pass
```

## Testes

- Adicione testes para novas funcionalidades
- Execute testes antes de fazer commit
- Mantenha cobertura acima de 80%

```bash
# Executar testes
docker-compose exec backend pytest

# Com cobertura
docker-compose exec backend pytest --cov=.
```

## Segurança

- Nunca commite credenciais ou tokens
- Use variáveis de ambiente
- Reporte vulnerabilidades privadamente

## Reportar Bugs

1. Verifique se o bug já foi reportado
2. Descreva o comportamento esperado vs atual
3. Forneça passos para reproduzir
4. Inclua logs relevantes

## Sugestões de Melhorias

- Abra uma issue para discussão
- Descreva o caso de uso
- Explique os benefícios

## Código de Conduta

- Seja respeitoso
- Aceite críticas construtivas
- Foque no código, não nas pessoas

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a MIT License.

---

Obrigado por contribuir! 🙏
