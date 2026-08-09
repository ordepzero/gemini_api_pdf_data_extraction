# AGENTS.md - Diretrizes da Arquitetura API + Streamlit

## Visão Geral da Arquitetura
O projeto adota uma arquitetura em camadas modular (*Core + Deliveries*):
1. `src/core/`: Núcleo da aplicação contendo regras de negócio, chamadas ao Gemini, modelos de banco de dados e schemas Pydantic. É 100% independente de Streamlit ou FastAPI.
2. `src/api/`: Camada de API REST desenvolvida com FastAPI para consumo externo (WhatsApp, Webhooks, etc.).
3. `src/web/`: Camada de interface de usuário utilizando Streamlit.

## Regras de Ouro
- **Independência do Core:** NUNCA importe bibliotecas de apresentação (`streamlit` ou `fastapi`) dentro dos arquivos de `src/core/`.
- **Reutilização de Regras:** Todas as lógicas de cálculo de m², validação de totais e extração de PDF via Gemini DEVEM residir em `src/core/services/`.
- **Rotas de API:** Todos os endpoints em `src/api/` devem apenas validar parâmetros via Pydantic, delegar a execução para `src/core/services/` e retornar a resposta JSON.
- **Camada Web:** O Streamlit em `src/web/` atua como cliente e deve importar funcionalidades do `src/core/` ou consumir os endpoints da API.

## Estrutura de Diretórios
- `src/rag_budget/app.py`: Ponto de entrada da interface Streamlit. Responsável apenas pela captura de inputs e exibição de componentes.
- `src/rag_budget/components/`: Componentes visuais modularizados do Streamlit.
- `src/rag_budget/services/`: Camada de regras de negócio e integrações externas (Gemini API, Cálculos de Precificação/m², Validações).
- `src/rag_budget/database/`: Camada de acesso a dados (Modelos de BD e operações de CRUD).
- `src/rag_budget/schemas/`: Contratos de dados e schemas Pydantic para validação do Gemini Structured Output.
- `src/rag_budget/config.py`: Gestão de variáveis de ambiente e configurações.

## Regras para Desenvolvimento de Código
1. **Interface Limpa**: O arquivo `app.py` NUNCA deve executar chamadas diretas a APIs externas ou queries de banco de dados. Sempre utilize os módulos em `services/` ou `database/`.
2. **Validação de Dados**: Toda comunicação estruturada com o Gemini DEVE utilizar schemas Pydantic definidos em `schemas/`.
3. **Tratamento de Exceções**: Serviços externos (Gemini/BD) devem possuir captura de exceções tratadas e relançadas com mensagens claras para a camada visual.
4. **Regra de Precificação**: Lógicas de cálculo de área ($m^2$), proporções ou perda técnica pertencem exclusivamente ao `services/pricing_engine.py`.
5. **Tipagem**: Todos os novos métodos e funções devem utilizar Type Hints do Python (`typing`).

## Arquitetura alvo
./
├── .env
├── AGENTS.md
├── requirements.txt
└── src/
    ├── core/                        # NÚCLEO COMPARTILHADO (Sem código de UI ou rotas HTTP)
    │   ├── config.py                # Configurações e variáveis de ambiente
    │   ├── database/                # Conexão e repositórios de banco de dados
    │   │   ├── connection.py
    │   │   ├── models.py
    │   │   └── repository.py
    │   ├── schemas/                 # Schemas Pydantic (Budget, Client, Item, etc.)
    │   │   └── budget_schema.py
    │   └── services/                # Regras de negócio puras
    │       ├── extractor.py         # Integração com Gemini
    │       ├── pricing_engine.py    # Calculadora de m² e perdas
    │       └── validator.py         # Validações de consistência do orçamento
    │
    ├── api/                         # CAMADA DE API (FastAPI)
    │   ├── main.py                  # Ponto de entrada do FastAPI
    │   └── routes/                  # Endpoints REST
    │       ├── budgets.py           # POST /budgets/extract, GET /budgets
    │       └── pricing.py           # POST /pricing/estimate
    │
    └── web/                         # CAMADA DE INTERFACE (Streamlit)
        ├── app.py                   # Ponto de entrada do Streamlit
        └── components/              # Componentes visuais
            ├── pdf_viewer.py
            └── review_form.py

## Stack Tecnológica
- **Python**: 3.10+
- **Frontend**: Streamlit
- **LLM / Extração**: Google Gemini API gemini-3.6-flash como padrão (Multimodal / Structured Outputs)
- **Validação de Dados**: Pydantic v2
- Use o python disponível em .venv


## Regra de Modelo Gemini
- O modelo padrao do projeto e gemini-3.6-flash.
- Nunca rebaixar para gemini-2.5-flash ou versao anterior sem solicitacao explicita do usuario.
- Nenhum fallback hardcoded de modelo Gemini pode existir fora de src/core/config.py.

