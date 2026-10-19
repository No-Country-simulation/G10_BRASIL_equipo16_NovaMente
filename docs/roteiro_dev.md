
---

## Roteiro de Desenvolvimento Planejado

```
[Etapa 1: Ingestão & RAG] ➔ [Etapa 2: Agentes & Prompts] ➔ [Etapa 3: Backend & Schema JSON]
                                                                      │
[Etapa 5: OCI & Documentação] ◄───────── [Etapa 4: Interface UI] ◄────┘

```

---

### 1. Etapa 1: Fundação do RAG (Ingestão e Busca Semântica)

> **Objetivo:** Garantir que o sistema consiga ler arquivos técnicos e buscar informações relevantes sem erros.

* [ ] **Configurar o ambiente Python:** Crie um ambiente virtual (`venv` ou `conda`) e instale bibliotecas base (`langchain`, `pypdf`, `chromadb` ou `faiss-cpu`, `sentence-transformers`).
* [ ] **Leitura de documentos:** Crie um script/módulo simples para ler arquivos `.pdf`, `.md` e `.txt` usando `PyPDF` ou carregadores nativos do LangChain.
* [ ] **Chunking & Embeddings:**
* Divida o texto em pedaços com `RecursiveCharacterTextSplitter` (ex: tamanho de chunk ~1000 com overlap de ~200).
* Escolha um modelo de embeddings (ex: OpenAI `text-embedding-3-small` ou HuggingFace `all-MiniLM-L6-v2` gratuito/local).


* [ ] **Vector Store:** Guarde os vetores em um banco de vetores local como **ChromaDB** ou **FAISS**.
* [ ] **Validação inicial:** Teste uma pergunta sobre o documento e verifique se os trechos recuperados (*retrieval*) são exatos e relevantes.

---

### 2. Etapa 2: Orquestração de Agentes e Prompts

> **Objetivo:** Desenvolver o fluxo de inteligência adaptativa (perfil, nicho, formato pedagógico e prevenção de alucinações).

* [ ] **Configurar conexão com LLM:** Escolha a API base (Google Gemini, OpenAI GPT-4o, Claude ou Ollama local).
* [ ] **Engenharia de Prompts:** Crie templates dinâmicos (*Role Prompting*) que recebam:
* `Perfil`: ex.: *Líder Técnico* vs. *Iniciante*.
* `Nicho`: ex.: *Fintech*, *Saúde*.
* `Formato`: ex.: *Quiz*, *Flashcards*, *Tutorial*.


* [ ] **Cadeia de Geração e Revisão (LangChain / LangGraph):**
* **Agente 1 (Redator):** Lê o contexto RAG e gera o conteúdo pedagógico.
* **Agente 2 (Revisor/Validador):** Verifica se o conteúdo gerado é fiel ao texto original e se condiz com o perfil solicitado.


* [ ] **Extração de Metadados:** Peça para a LLM gerar também pré-requisitos, tempo estimado de estudo e termos-chave.

---

### 3. Etapa 3: Estruturação dos Dados (JSON & Schemas)

> **Objetivo:** Garantir que o resultado final seja previsível e padronizado para integração.

* [ ] **Definir o Schema com Pydantic:**
Crie um modelo estrito de dados em Python:
```python
from pydantic import BaseModel
from typing import List

class ConteudoEducacional(BaseModel):
    titulo: str
    perfil_destinatario: str
    tempo_estimado_minutos: int
    conceitos_chave: List[str]
    pre_requisitos: List[str]
    conteudo_principal: str # Ou estrutura específica para quiz/flashcard

```


* [ ] **Saída Estruturada:** Utilize recursos como `Structured Output` (do LangChain/LLMs) ou `PydanticOutputParser` para garantir que a LLM sempre devolva um JSON válido.

---

### 4. Etapa 4: Interface do Usuário (Streamlit / Gradio)

> **Objetivo:** Dar vida à aplicação com um painel interativo simples e funcional.

* [ ] **Criar a UI base (ex.: Streamlit):**
* **Sidebar:** Upload do arquivo (`.pdf`, `.md`, `.txt`) e formulário com os menus suspensos (*dropdowns*) para Perfil, Nicho e Formato.
* **Área Principal:** Botão *"Gerar Conteúdo"*, indicador de carregamento (*spinner*) e exibição do resultado formatado.


* [ ] **Conectar UI ao Backend:** Integre a interface diretamente com o pipeline construído nas etapas 1 a 3.
* [ ] **Tratamento de Exceções:** Adicione alertas amigáveis caso o arquivo esteja corrompido, a API falhe ou a LLM devolva algo fora do esperado.

---

### 5. Etapa 5: Integração com OCI (Nuvem) & Documentação

> **Objetivo:** Cumprir os requisitos obrigatórios de infraestrutura e finalizar o projeto.

* [ ] **OCI Object Storage (Obrigatório):**
* Criar a conta na Oracle Cloud (tier *Always Free*) e criar um **Bucket**.
* Instale o SDK da Oracle (`oci` em Python).
* Configure as credenciais no código (via `.env` para não expor chaves).
* **Fluxo de Persistência:**
1. Ao receber o arquivo na UI, envie uma cópia para o Bucket OCI.
2. Ao gerar o JSON final, salve o pacote no Bucket OCI.
* [ ] *(Opcional)* **OCI Compute Instance:** Suba uma instância VM Linux na OCI Always Free e faça o deploy da sua aplicação Streamlit.
* [ ] **Repositório & README.md:**
* Grave uma breve demonstração com 3 cenários distintos para o mesmo documento original.



---
