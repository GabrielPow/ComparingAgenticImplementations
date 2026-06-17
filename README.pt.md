<div style="text-align: right;">
  <a href="README.md">English</a> | <a href="README.pt.md">Português</a>
</div>

# Comparando Implementações Agênticas

## Propósito
Este projeto compara dois estilos de implementação agêntica para resolver problemas de raciocínio jurídico e conformidade usando o Google Gemini.

O objetivo é avaliar qual arquitetura funciona melhor para tarefas de raciocínio jurídico cada vez mais complexas, usando o framework regulatório brasileiro NR-1 como exemplo de domínio.

## O que queremos resolver
Estamos usando o direito como um domínio de casos extremos para comparar o comportamento agêntico em quatro níveis de dificuldade:

- Nível 1 — Definicional
  - "O que significa X no artigo Y?"
  - Um único artigo, um único conceito, resposta verificável
- Nível 2 — Interpretativo
  - "Como o artigo X se aplica à situação Y?"
  - Requer raciocínio sobre uma lei
- Nível 3 — Cruzado-referencial
  - "Este caso é coberto pela lei X ou pela lei Y?"
  - Multi-hop, requer comparar entre códigos
- Nível 4 — Conflitantes/Casos de borda
  - "Dado X e Y, qual lei prevalece e por quê?"
  - Requer raciocínio jurídico, hierarquia de normas

## Visão geral da arquitetura
Este repositório contém duas arquiteturas separadas para análise agêntica de conformidade.

### 1) `Multi-Agents`

`Multi-Agents` usa um pipeline explícito de múltiplos agentes:

- `Multi-Agents/main.py`
  - Ponto de entrada que carrega o framework NR-1 e os dados do documento da empresa.
  - Envia uma consulta de conformidade para o orquestrador.
- `Multi-Agents/agents/agents.py`
  - `OrchestratorAgent`: orquestra o fluxo de trabalho.
  - `RetrieverAgent`: recupera as cláusulas legais relevantes.
  - `ComplianceAgent`: realiza análise de lacunas.
  - `QAValidationAgent`: valida a análise.
- `Multi-Agents/agents/gemini_ai.py`
  - Implementa as chamadas Gemini para cada função de agente.
  - Separa decomposição, recuperação, raciocínio e validação.

Esta arquitetura é melhor quando você quer:

- separação clara de papéis
- etapas de raciocínio modulares
- visibilidade explícita do pipeline
- melhor rastreabilidade e inspeção de cada etapa

### 2) `Multi-Tools`

`Multi-Tools` usa um único agente com raciocínio baseado em ferramentas:

- `Multi-Tools/main.py`
  - Ponto de entrada que emite uma consulta de conformidade ao único `compliance_agent`.
- `Multi-Tools/agents/gemini_ai.py`
  - Define um único loop de agente Gemini.
  - O modelo pode invocar chamadas de ferramentas durante a sessão.
- `Multi-Tools/skills/gemini_tools.py`
  - Define três ferramentas:
    - `retrieval_fetch_tool`
    - `reasoning_comparison_tool`
    - `validation_tool`
  - As ferramentas são declaradas ao Gemini e executadas a partir do Python.

Esta arquitetura é melhor quando você quer:

- orquestração flexível orientada pelo modelo
- capacidades especificadas por ferramentas
- uma superfície de código menor para gerenciamento do agente
- tomada de decisão interna do modelo sobre o uso de ferramentas

## Dados e domínio de exemplo

- `data/nr1_clauses.py`
  - Contém os dados do framework regulatório NR-1 usados para consultas de conformidade.
  - Também fornece conteúdo de documento da empresa para análise de lacunas.

O domínio é intencionalmente focado em jurídico/conformidade para que possamos testar raciocínio agêntico em:

- recuperação de texto exata
- interpretação normativa
- comparação cruzada de referências
- resolução de conflitos e hierarquia de normas

## Como executar

1. Adicione sua chave de API Gemini em `.env` tanto em `Multi-Agents` quanto em `Multi-Tools`, se necessário:

```env
GEMINI_API_KEY=your_api_key_here
```

2. Execute o pipeline multi-agente:

```bash
python Multi-Agents/main.py
```

3. Execute o pipeline de ferramenta com um único agente:

```bash
python Multi-Tools/main.py
```

## Estratégia de avaliação

Use o mesmo conjunto de consultas de raciocínio jurídico em ambas as implementações e compare:

- qualidade da recuperação
- transparência da cadeia de pensamento
- correção em questões definicionais
- capacidade de interpretar uma única lei
- capacidade de comparar várias leis
- capacidade de resolver normas conflitantes
- taxa de alucinação e confiança da validação

### Fluxo de teste sugerido

1. Comece com uma consulta de nível 1 definicional para validar a precisão da recuperação.
2. Passe para uma consulta de nível 2 interpretativa para testar o raciocínio sobre uma lei.
3. Use uma consulta de nível 3 cruzado-referencial para forçar comparação multi-hop.
4. Termine com uma consulta de nível 4 de conflito para avaliar o raciocínio sobre hierarquia jurídica.

## O que comparar

- `Multi-Agents` fornece sub-agentes explícitos e inspecionáveis e é bom para fluxos de trabalho estruturados.
- `Multi-Tools` fornece invocação de ferramentas orientada pelo modelo e é bom para raciocínio adaptativo com ferramentas.

Use o exemplo jurídico como um ambiente de teste para decidir qual abordagem é melhor para:

- fluxos de trabalho de conformidade estrita
- casos de borda de raciocínio jurídico
- entradas adversariais ou conflitantes
- explicabilidade versus flexibilidade de ferramentas

## Observações

A implementação atual usa Gemini 2.5 Flash e um pequeno conjunto de dados de conformidade NR-1. O mesmo padrão pode ser estendido para outros códigos legais ou domínios regulatórios.

> Nota: um front-end Streamlit em `app.py` será implementado em breve para simplificar ambas as arquiteturas em uma interface unificada. O design atual é intencionalmente exploratório e a arquitetura pode evoluir à medida que os testes revelarem a melhor abordagem agêntica.
