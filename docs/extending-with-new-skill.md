# Como Estender sdd-ollama com Novos Skills

## Visão Geral

Este documento guia você através da criação de um novo **Skill** para o pipeline do sdd-ollama.

Um **Skill** é um componente reutilizável que executa uma etapa específica da geração de artigos. Atualmente existem:

- **Researcher** - Pesquisa web e extração de dados
- **Analyst** - Análise técnica estruturada
- **Writer** - Geração de artigo em Markdown
- **Critic** - Validação contra a spec

## Anatomia de um Skill

Todos os skills compartilham a mesma estrutura:

```python
import yaml
import logging
from pathlib import Path
from llm import LLMClient

logger = logging.getLogger(__name__)

class MyNewSkill:
    
    def __init__(self, memory, spec_path="spec/article_spec.yaml"):
        self.memory = memory
        self.spec = yaml.safe_load(Path(spec_path).read_text())
        self.llm = LLMClient(spec_path)
        self.model = self.llm.model_for_role("my_role")
        
        llm_conf = self.spec.get("llm", {})
        temperatures = llm_conf.get("temperature", {})
        timeouts = llm_conf.get("timeout", {})
        
        self.temp = temperatures.get("my_role", 0.1)
        self.timeout = timeouts.get("my_role", timeouts.get("default", 300))
    
    def run(self, **kwargs):
        """Executa a lógica do skill."""
        logger.debug(f"Starting my_role with: {kwargs}")
        
        # Sua lógica aqui
        
        logger.debug(f"Completed my_role")
        
        self.memory.log_event("my_role_done", {
            "key": "value",
        })
        
        return result
```

## Passo 1: Criar o Arquivo do Skill

```bash
touch skills/my_new_skill.py
```

## Passo 2: Implementar a Classe

```python
# skills/my_new_skill.py
import yaml
import logging
from pathlib import Path
from llm import LLMClient

logger = logging.getLogger(__name__)

class MyNewSkill:
    
    def __init__(self, memory, spec_path="spec/article_spec.yaml"):
        self.memory = memory
        self.spec = yaml.safe_load(Path(spec_path).read_text())
        self.llm = LLMClient(spec_path)
        self.model = self.llm.model_for_role("my_role")
        
        llm_conf = self.spec.get("llm", {})
        temperatures = llm_conf.get("temperature", {})
        timeouts = llm_conf.get("timeout", {})
        
        self.temp = temperatures.get("my_role", 0.1)
        self.timeout = timeouts.get("my_role", timeouts.get("default", 300))
    
    def run(self, input_data, additional_param="default"):
        """
        Executa a lógica do skill.
        
        Args:
            input_data: Dados de entrada
            additional_param: Parâmetro opcional
        
        Returns:
            str: Resultado processado
        """
        logger.debug(f"Starting my_role with input_data={len(input_data)} chars")
        
        # Lógica principal
        prompt = f"""Seu prompt aqui.
        
Input: {input_data}
Param: {additional_param}
"""
        
        logger.debug(f"Calling LLM (timeout: {self.timeout}s, temp: {self.temp})")
        resp = self.llm.generate(
            role="my_role",
            model=self.model,
            prompt=prompt,
            temperature=self.temp,
            timeout=self.timeout,
        )
        logger.debug(f"LLM response: {len(resp.response)} chars")
        
        # Log do evento
        self.memory.log_event("my_role_done", {
            "input_length": len(input_data),
            "output_length": len(resp.response),
            "param": additional_param,
        })
        
        return resp.response
```

## Passo 3: Registrar na Pipeline

Abra `pipeline.py` e adicione:

```python
# pipeline.py - no __init__
from skills.my_new_skill import MyNewSkill

class SDDPipeline:
    def __init__(self, spec_path: str = "spec/article_spec.yaml"):
        # ... código existente ...
        
        # Adicionar seu skill
        self.my_new_skill = MyNewSkill(self.memory, spec_path)
    
    def run(self, ferramentas, contexto, foco="comparação geral", questoes=None):
        # ... código existente ...
        
        # Chamar seu skill onde fizer sentido
        self.log.section(2, 4, "Executando Novo Skill")
        with self.log.task("Executando my_new_skill"):
            try:
                my_result = self.my_new_skill.run(
                    input_data=research,
                    additional_param="value"
                )
            except TimeoutException:
                self.log.error(f"my_new_skill timeout")
                my_result = "Timeout"
        
        # ... resto do código ...
```

## Passo 4: Configurar na Spec

Adicione a configuração do seu skill em `spec/article_spec.yaml`:

```yaml
llm:
  timeout:
    my_role: 600        # timeout específico
  temperature:
    my_role: 0.1        # temperatura (criatividade)
  context_length:
    my_role: 8192       # tamanho máximo de contexto
```

## Passo 5: Criar Testes

```python
# tests/test_my_new_skill.py
import pytest
from unittest.mock import Mock, patch
from skills.my_new_skill import MyNewSkill

@pytest.mark.deterministic
@patch('skills.my_new_skill.LLMClient')
def test_my_new_skill_basic(mock_llm_class):
    # Arrange
    mock_instance = Mock()
    mock_instance.model_for_role.return_value = "test-model"
    mock_instance.generate.return_value = Mock(response="Test response")
    mock_llm_class.return_value = mock_instance
    
    mock_memory = Mock()
    mock_memory.get_lessons_for_prompt.return_value = ""
    
    skill = MyNewSkill(mock_memory)
    
    # Act
    result = skill.run("input data", additional_param="test")
    
    # Assert
    assert mock_instance.generate.called
    assert isinstance(result, str)

@pytest.mark.deterministic
def test_my_new_skill_init():
    """Testa inicialização do skill."""
    mock_memory = Mock()
    skill = MyNewSkill(mock_memory)
    
    assert skill.model is not None
    assert skill.timeout > 0
    assert skill.temp >= 0
```

## Passo 6: Rodar Testes

```bash
# Rodar apenas testes do novo skill
uv run pytest tests/test_my_new_skill.py -v

# Rodar com cobertura
uv run pytest tests/test_my_new_skill.py --cov=skills.my_new_skill

# Rodar apenas determinísticos (rápido)
uv run pytest -m deterministic -v
```

## Padrões e Boas Práticas

### 1. Logging

```python
logger.debug(f"Starting with: {param}")
logger.debug(f"LLM response: {len(response)} chars")
logger.warning(f"Unexpected condition detected")
logger.error(f"Error occurred: {exception}")
```

### 2. Memory Logging

```python
self.memory.log_event("skill_name_done", {
    "input_metric": value,
    "output_metric": value,
    "context": "relevant info"
})
```

### 3. Error Handling

```python
try:
    resp = self.llm.generate(...)
except TimeoutException:
    logger.error(f"Timeout after {self.timeout}s")
    # Retornar fallback ou relançar
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### 4. Timeout Handling

```python
# Sempre respeitar timeout da spec
logger.debug(f"Calling LLM (timeout: {self.timeout}s)")
resp = self.llm.generate(
    role=self.role,
    model=self.model,
    prompt=prompt,
    temperature=self.temp,
    timeout=self.timeout,  # Crítico!
)
```

## Exemplo Completo: Skill Hypothetical

Digamos que você quer criar um skill chamado **Optimizer** que otimiza prompts:

```python
# skills/optimizer.py
import yaml
import logging
from pathlib import Path
from llm import LLMClient

logger = logging.getLogger(__name__)

class OptimizerSkill:
    """Otimiza prompts para melhor qualidade de resposta."""
    
    def __init__(self, memory, spec_path="spec/article_spec.yaml"):
        self.memory = memory
        self.spec = yaml.safe_load(Path(spec_path).read_text())
        self.llm = LLMClient(spec_path)
        self.model = self.llm.model_for_role("optimizer")
        
        llm_conf = self.spec.get("llm", {})
        temperatures = llm_conf.get("temperature", {})
        timeouts = llm_conf.get("timeout", {})
        
        self.temp = temperatures.get("optimizer", 0.0)  # Determinístico
        self.timeout = timeouts.get("optimizer", timeouts.get("default", 300))
    
    def run(self, article, validation_feedback):
        """
        Otimiza artigo baseado em feedback.
        
        Args:
            article: Artigo a otimizar
            validation_feedback: Feedback da validação
        
        Returns:
            str: Artigo otimizado
        """
        logger.debug(f"Optimizing article ({len(article)} chars) with feedback")
        
        prompt = f"""Otimize este artigo seguindo o feedback:

ARTIGO:
{article}

FEEDBACK:
{validation_feedback}

REGRAS:
- Faça APENAS as correções sugeridas
- Mantenha o estilo e estrutura
- Não mude seções inteiras sem motivo
"""
        
        logger.debug(f"Calling LLM (timeout: {self.timeout}s)")
        resp = self.llm.generate(
            role="optimizer",
            model=self.model,
            prompt=prompt,
            temperature=self.temp,
            timeout=self.timeout,
        )
        logger.debug(f"Optimized: {len(resp.response)} chars")
        
        self.memory.log_event("optimization_done", {
            "original_len": len(article),
            "optimized_len": len(resp.response),
            "feedback_used": len(validation_feedback),
        })
        
        return resp.response
```

```python
# tests/test_optimizer.py
import pytest
from unittest.mock import Mock, patch
from skills.optimizer import OptimizerSkill

@pytest.mark.deterministic
@patch('skills.optimizer.LLMClient')
def test_optimizer_basic(mock_llm_class):
    mock_instance = Mock()
    mock_instance.model_for_role.return_value = "opt-model"
    mock_instance.generate.return_value = Mock(response="Optimized article")
    mock_llm_class.return_value = mock_instance
    
    mock_memory = Mock()
    
    skill = OptimizerSkill(mock_memory)
    result = skill.run("Original article", "Fix section X")
    
    assert "Optimized" in result
    assert mock_memory.log_event.called
```

## Integração no Pipeline

```python
# pipeline.py
def run(self, ferramentas, contexto, foco="comparação geral", questoes=None):
    # ... research, analysis, writer ...
    
    # Nova etapa: Otimização
    self.log.section(4, 4, "Otimizando")
    with self.log.task("Otimizando artigo"):
        try:
            article = self.optimizer.run(article, correction_instructions)
        except TimeoutException:
            self.log.error("Optimizer timeout")
    
    # ... resto do pipeline ...
```

## Checklist de Implementação

- [ ] Criar arquivo `skills/my_new_skill.py`
- [ ] Implementar classe com `__init__` e `run`
- [ ] Adicionar logging (debug level)
- [ ] Adicionar memory events
- [ ] Registrar em `pipeline.py`
- [ ] Adicionar configuração em `spec/article_spec.yaml`
- [ ] Criar testes em `tests/test_my_new_skill.py`
- [ ] Executar testes (mínimo 70% cobertura)
- [ ] Documentar parâmetros
- [ ] Testar timeout gracefully
- [ ] Integrar no pipeline.run()
- [ ] Testar fim-a-fim

## Debugging

Ativar logs em DEBUG:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

Verificar eventos de memória:

```bash
tail -50 .memory/*.json
```

Rodar testes com verbose output:

```bash
uv run pytest tests/test_my_new_skill.py -vv -s
```

## Próximos Passos

Após implementar seu skill:

1. Envie um PR com testes
2. Solicite revisão da documentação
3. Merge e deploy
4. Monitor em produção

## Perguntas Frequentes

**P: Qual temperatura usar?**
R: 0.0-0.3 para determinístico, 0.5+ para criativo

**P: Como mockear LLMClient em testes?**
R: Veja `tests/test_skills_mocked.py` para exemplos

**P: Preciso respeitar timeout?**
R: Sim! Sempre passe `timeout=self.timeout` ao chamar LLM

**P: Posso adicionar dependências?**
R: Sim, mas documente em pyproject.toml

---

**Happy extending!** 🚀
