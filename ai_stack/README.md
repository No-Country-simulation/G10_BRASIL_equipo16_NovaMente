# NovaMente --- AI Stack

Camada de inteligência artificial do **NovaMente --- Sistema Inteligente
de Adaptação e Geração de Conteúdo Educacional**, desenvolvido no âmbito
do **ONE AI FOR TECH**.

A AI Stack processa documentos, recupera conhecimento relevante, gera
materiais educativos estruturados e avalia a qualidade dos conteúdos
produzidos.

> **Estado atual:** pipeline RAG implementado com ingestão documental,
> embeddings locais, Chroma, recuperação semântica, geração estruturada
> com LLM, schemas Pydantic e agentes Reviewer/Corrector. O ciclo de
> revisão e correção tem um limite definido. A execução integrada
> reportada gerou flashcards e recebeu aprovação do Reviewer.

------------------------------------------------------------------------

## 1. Visão geral

A AI Stack transforma documentação técnica em materiais educativos
adaptados ao perfil e ao nível de conhecimento do estudante.

O sistema combina três capacidades:

-   **RAG:** recupera fragmentos relevantes dos documentos usados como
    fonte.
-   **Geração estruturada:** utiliza um LLM para produzir flashcards,
    quizzes ou tutoriais segundo contratos Pydantic.
-   **Revisão automática:** avalia conteúdos de quiz e flashcards e,
    quando necessário, solicita uma correção.

Princípios de funcionamento:

1.  **Fidelidade à fonte:** a geração deve ser fundamentada no contexto
    recuperado.
2.  **Adaptação pedagógica:** linguagem e profundidade devem respeitar o
    perfil solicitado.
3.  **Consistência estrutural:** as respostas devem cumprir os schemas
    definidos.
4.  **Controlo de qualidade:** conteúdos abrangidos pelo Reviewer só são
    considerados aprovados após revisão positiva.

## 2. Arquitetura e estrutura

``` text
ai_stack/
├── agents/
│   ├── reviewer.py
│   ├── reviewer_prompts.py
│   └── __init__.py
├── ingestion/
│   ├── chunking.py
│   ├── document_identity.py
│   ├── embeddings.py
│   ├── loader.py
│   ├── vector_store.py
│   └── __init__.py
├── config.py
├── generator_prompts.py
├── llm.py
├── main.py
├── rag_pipeline.py
├── retrieval.py
├── schemas.py
└── README.md
```

  -----------------------------------------------------------------------
  Módulo                              Responsabilidade
  ----------------------------------- -----------------------------------
  `config.py`                         Centraliza parâmetros de chunking,
                                      embeddings, LLM e caminhos.

  `ingestion/loader.py`               Carrega documentos PDF, TXT e
                                      Markdown.

  `ingestion/chunking.py`             Divide documentos e preserva
                                      metadados dos fragmentos.

  `ingestion/document_identity.py`    Identifica documentos, conteúdos e
                                      versões.

  `ingestion/embeddings.py`           Inicializa o modelo local de
                                      embeddings.

  `ingestion/vector_store.py`         Integra a ingestão e a persistência
                                      com Chroma.

  `retrieval.py`                      Recupera os fragmentos mais
                                      relevantes para uma pergunta.

  `llm.py`                            Encapsula as chamadas ao modelo
                                      disponibilizado pela Groq.

  `generator_prompts.py`              Define as instruções de geração e
                                      correção.

  `schemas.py`                        Define os contratos Pydantic dos
                                      conteúdos e relatórios.

  `agents/reviewer.py`                Avalia os conteúdos educativos e
                                      produz relatórios.

  `rag_pipeline.py`                   Coordena recuperação, geração,
                                      validação, revisão e correção.

  `main.py`                           Executa a demonstração integrada da
                                      AI Stack.
  -----------------------------------------------------------------------

### 2.1. Fluxo de execução

``` mermaid
flowchart TD
    A[Documentos PDF, TXT e Markdown] --> B[Loader]
    B --> C[Chunking e metadados]
    C --> D[Embeddings locais]
    D --> E[(Chroma)]

    F[Pergunta e perfil] --> G[Retrieval]
    E --> G
    G --> H[Contexto recuperado]
    H --> I[Prompt de geração]
    I --> J[LLM via Groq]
    J --> K[JSON]
    K --> L[EducationalPackage]

    L --> M{Formato}
    M -->|Tutorial| N[Resultado validado]
    M -->|Quiz ou flashcards| O[Reviewer]
    O --> P{Estado}
    P -->|approved| Q[success]
    P -->|correction_required| R[Corrector]
    R --> S[Validar pacote corrigido]
    S --> O
    O -->|Limite atingido sem aprovação| T[requires_manual_review]
```

O diagrama representa o fluxo documentado da AI Stack. A persistência na
OCI Object Storage não está incluída, pois é uma integração futura.

## 3. Ingestão documental

A ingestão converte os documentos de origem em fragmentos preparados
para pesquisa semântica.

### 3.1. Carregamento

O `loader.py` suporta:

-   PDF;
-   TXT;
-   Markdown.

Os carregadores do LangChain convertem os ficheiros em objetos
`Document`, preservando metadados como origem e página, quando
disponíveis.

### 3.2. Chunking

O `chunking.py` utiliza `RecursiveCharacterTextSplitter` para dividir o
texto, dando prioridade a separadores maiores --- como parágrafos e
quebras de linha --- antes de recorrer a divisões menores.

Os fragmentos preservam metadados de rastreabilidade, incluindo:

-   origem e página;
-   índice do fragmento;
-   identificador do documento e do fragmento;
-   versão do documento.

A divisão recursiva ajuda a preservar a continuidade textual, mas não
garante unidades semânticas completas. Os parâmetros de tamanho e
sobreposição são configurados em `config.py`.

### 3.3. Identidade e versionamento

O `document_identity.py` identifica documentos e versões com base no
conteúdo. Assim, uma alteração pode ser reconhecida mesmo quando o nome
do ficheiro permanece igual.

**Limitação:** identificar uma nova versão não significa eliminar
automaticamente os fragmentos da versão anterior. A gestão e remoção de
fragmentos obsoletos ainda precisam de ser consolidadas.

## 4. Embeddings e armazenamento vetorial

### 4.1. Embeddings

Modelo utilizado:

``` text
sentence-transformers/all-MiniLM-L6-v2
```

O modelo converte textos em vetores que permitem comparar semanticamente
perguntas e fragmentos. A execução é local, sem necessidade de uma API
externa para gerar embeddings.

A escolha privilegia leveza e facilidade de integração. A adequação ao
português ainda precisa de ser avaliada com documentos e perguntas
representativas.

Na primeira execução, o modelo pode ser descarregado do Hugging Face; é
necessária ligação à Internet caso ainda não esteja disponível
localmente.

### 4.2. Chroma

O `vector_store.py` integra o Chroma para:

-   armazenar embeddings e fragmentos;
-   preservar metadados e identificadores;
-   manter a base vetorial persistente localmente;
-   apoiar a ingestão incremental.

A escolha deve-se à integração com LangChain, simplicidade e adequação
ao estágio atual do projeto. A persistência local não equivale, por si
só, a uma arquitetura distribuída ou preparada para qualquer cenário de
produção.

## 5. Recuperação semântica

O `retrieval.py` disponibiliza `recuperar_documentos_relevantes()`, que
recebe a base vetorial, a pergunta e a quantidade de fragmentos a
recuperar.

O pipeline utiliza atualmente **três fragmentos (`k=3`)**.

Este valor procura equilibrar relevância, quantidade de contexto e
consumo de tokens. É uma configuração inicial, não um resultado de
benchmark. Três fragmentos podem ser insuficientes quando uma pergunta
depende de informação distribuída por várias partes dos documentos.

A qualidade da recuperação deve ser avaliada com perguntas de referência
e comparação entre diferentes valores de `k`.

## 6. Geração e integração com o LLM

O `llm.py` encapsula a comunicação com o modelo de linguagem através da
Groq. A credencial é obtida pela variável de ambiente `GROQ_API_KEY`.

O `generator_prompts.py` define:

-   `generation_prompt`: orienta a geração a partir do contexto
    recuperado;
-   `correction_prompt`: orienta a correção a partir do pacote e dos
    problemas identificados pelo Reviewer.

O prompt de geração estabelece requisitos de utilização do contexto,
idioma, adaptação ao perfil e formato solicitado. A resposta esperada é
um objeto JSON com `metadata` e `content`.

A separação do acesso ao LLM num módulo próprio evita espalhar a
integração com o fornecedor pelos restantes componentes.

## 7. Schemas e validação

O `schemas.py` define os contratos de dados através de Pydantic.

### 7.1. Modelos principais

  -----------------------------------------------------------------------
  Modelo                              Responsabilidade
  ----------------------------------- -----------------------------------
  `NovaMenteBaseModel`                Configuração base dos modelos.

  `Formats`                           Enumeração dos formatos suportados.

  `EducationMetadata`                 Metadados educativos e perfil
                                      aplicado.

  `FlashCard` / `FlashcardContent`    Cartão individual e conjunto de
                                      flashcards.

  `QuizOption` / `QuizQuestion` /     Opções, perguntas e estrutura do
  `QuizContent`                       quiz.

  `TutorialStep` / `TutorialContent`  Etapas e estrutura do tutorial.

  `EducationalPackage`                Associa metadados ao conteúdo do
                                      formato declarado.
  -----------------------------------------------------------------------

### 7.2. Formatos

-   **Flashcards:** cada cartão contém `card_id`, `front` e `back`. O
    schema exige cartões e impede identificadores duplicados.
-   **Quiz:** cada pergunta contém enunciado, opções, identificador da
    resposta correta e justificação. A validação verifica
    identificadores e a existência da opção correta.
-   **Tutorial:** contém título, introdução e uma ou mais etapas, cada
    uma com título, explicação e exemplo opcional.

### 7.3. Metadados e limites da validação

`EducationMetadata` inclui:

-   `profile_applied`: `iniciante` ou `intermediario`;
-   `format_generated`;
-   `key_concepts`;
-   `study_time_minutes`;
-   `prerequisites`.

O `EducationalPackage` verifica se o formato declarado corresponde ao
tipo de conteúdo fornecido.

Os schemas validam estrutura, tipos e regras explicitamente programadas.
Não garantem, por si só, correção factual, qualidade pedagógica,
cobertura de todos os conceitos ou ausência de redundância. Também não
existe uma exigência de correspondência de um para um entre
`key_concepts` e flashcards.

## 8. Agentes: Reviewer e Corrector

### 8.1. Reviewer

O Reviewer, implementado em `agents/reviewer.py` e instruído por
`agents/reviewer_prompts.py`, avalia o conteúdo como um todo e produz um
relatório estruturado.

Critérios:

  Critério                Objetivo
  ----------------------- ---------------------------------------------
  `source_fidelity`       Avaliar a fidelidade às fontes recuperadas.
  `technical_accuracy`    Avaliar a precisão técnica.
  `ambiguity`             Identificar ambiguidades.
  `pedagogical_quality`   Avaliar a qualidade pedagógica.

Estados possíveis:

-   `approved`: conteúdo aprovado;
-   `correction_required`: foram identificados problemas que exigem
    correção.

O relatório inclui estado, resumo e problemas. Cada problema pode
identificar o elemento afetado, tipo, categoria, descrição, evidência e
sugestão.

O Reviewer identifica problemas; não altera diretamente o conteúdo.

**Âmbito atual:** o ciclo de revisão está integrado para `quiz` e
`flashcards`. Os tutoriais passam por validação estrutural, mas não pelo
mesmo ciclo de revisão automática.

### 8.2. Corrector e ciclo de revisão

O Corrector utiliza o relatório do Reviewer para produzir uma nova
versão do pacote. A coordenação do processo está em `rag_pipeline.py`.

O limite atual é:

``` python
MAX_RODADAS_CORRECAO = 2
```

Fluxo:

1.  O LLM gera o conteúdo.
2.  O `EducationalPackage` valida a estrutura.
3.  Para quiz e flashcards, o Reviewer avalia o conteúdo.
4.  Se aprovado, o pipeline termina com `success`.
5.  Se exigir correção, o relatório é enviado ao Corrector.
6.  A versão corrigida é novamente validada e revista.
7.  O processo termina quando existe aprovação ou quando o limite é
    atingido.

O limite controla chamadas ao LLM, consumo de tokens e tempo de
execução. Se o conteúdo continuar reprovado, o pipeline devolve
`requires_manual_review`, indicando necessidade de intervenção humana.

### 8.3. Estados de saída

  -----------------------------------------------------------------------
  Estado                              Significado
  ----------------------------------- -----------------------------------
  `success`                           Conteúdo gerado e validado; nos
                                      formatos abrangidos, também
                                      aprovado pelo Reviewer.

  `insufficient_context`              Contexto documental insuficiente
                                      para fundamentar a geração.

  `requires_manual_review`            O conteúdo continua a necessitar de
                                      correção após o limite definido.
  -----------------------------------------------------------------------

A resposta do pipeline pode incluir `status`, `answer`, `sources`,
`message` e `review_report`.

Para tutoriais, `success` indica validação estrutural concluída; não
significa aprovação pelo Reviewer.

## 9. Tecnologias

  Tecnologia              Utilização
  ----------------------- ------------------------------------------------------------
  Python                  Implementação da AI Stack.
  LangChain               Carregamento, divisão, mensagens e integração RAG.
  Sentence Transformers   Geração local de embeddings.
  Chroma                  Persistência vetorial e pesquisa semântica.
  Groq                    Acesso ao modelo de linguagem.
  Pydantic                Schemas e validação.
  PyMuPDF                 Leitura de documentos PDF através do carregador utilizado.
  pytest                  Testes automatizados.

As dependências e versões devem ser consultadas no `requirements.txt` da
raiz do repositório.

## 10. Instalação e execução

Executar os comandos a partir da raiz do repositório.

### 10.1. Ambiente virtual e dependências

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 10.2. Configuração da Groq

Criar um ficheiro `.env` na raiz:

``` dotenv
GROQ_API_KEY=coloca_a_tua_chave_aqui
```

Não publicar o `.env`, incluir credenciais no Git ou expor chaves em
logs. Confirmar que `.env` está incluído no `.gitignore`.

### 10.3. Executar

Colocar os documentos no diretório definido por `RAG_SOURCE_PATH` e
executar:

``` powershell
python -m ai_stack.main
```

A base vetorial é persistida no caminho definido por `CHROMA_DB_PATH`. A
demonstração apresenta informação da ingestão, estado do pipeline,
relatório do Reviewer e conteúdo gerado, quando disponíveis.

## 11. Testes automatizados

Os testes estão no diretório `tests/`:

``` text
tests/
├── test_rag_pipeline.py
├── test_reviewer.py
├── test_review_schema.py
└── test_schema.py
```

Executar toda a suite:

``` powershell
python -m pytest tests/ -v
```

Executar um módulo:

``` powershell
python -m pytest tests/test_schema.py -v
```

  -----------------------------------------------------------------------
  Ficheiro                            Área validada
  ----------------------------------- -----------------------------------
  `test_schema.py`                    Schemas dos conteúdos educativos.

  `test_review_schema.py`             Estrutura dos relatórios de
                                      revisão.

  `test_reviewer.py`                  Comportamento do Reviewer.

  `test_rag_pipeline.py`              Geração, revisão, correção e
                                      estados do pipeline.
  -----------------------------------------------------------------------

**Último resultado reportado:** `37 passed, 13 warnings` em 3 segundos.
Os warnings não representam testes falhados; a sua origem deve ser
consultada no output completo do pytest.

### 11.1. Execução integrada reportada

Foi também reportada uma execução de `python -m ai_stack.main` com:

-   ingestão concluída;
-   518 fragmentos presentes na base vetorial;
-   geração de flashcards concluída;
-   `EducationalPackage` validado;
-   Reviewer com estado `approved`;
-   pipeline com estado `success`.

Este resultado demonstra o fluxo integrado no cenário testado, mas não
constitui uma avaliação abrangente da qualidade do sistema.

## 12. Limitações conhecidas

-   **Recuperação:** similaridade vetorial não garante que os fragmentos
    respondam integralmente à pergunta; `k=3` ainda não foi avaliado por
    benchmark.
-   **Versionamento:** novas versões são identificadas, mas a remoção
    automática de fragmentos antigos ainda precisa de ser consolidada.
-   **Embeddings:** a adequação de `all-MiniLM-L6-v2` ao português
    precisa de avaliação com dados representativos.
-   **Validação:** Pydantic garante contratos estruturais, não correção
    factual ou qualidade pedagógica.
-   **Reviewer:** a avaliação depende dos critérios, prompts e respostas
    do modelo.
-   **Tutoriais:** ainda não estão abrangidos pelo ciclo automático de
    revisão.
-   **Geração:** o LLM pode devolver JSON inválido ou conteúdo
    incompatível com os requisitos; a validação estrutural não elimina
    esse risco.
-   **Flashcards:** o sistema não exige correspondência 1:1 entre
    conceitos-chave e cartões, nem garante automaticamente cobertura ou
    ausência de redundância.

## 13. Decisões técnicas

  ----------------------------------------------------------------------------------
  Decisão                            Justificação            Ponto a avaliar
  ---------------------------------- ----------------------- -----------------------
  `RecursiveCharacterTextSplitter`   Tenta preservar         Ajustar tamanho e
                                     parágrafos e            sobreposição com
                                     continuidade textual.   documentos reais.

  Identidade e versão por conteúdo   Distingue alterações    Remover fragmentos
                                     mesmo quando o nome do  obsoletos.
                                     ficheiro não muda.

  `all-MiniLM-L6-v2`                 Modelo local, leve e    Medir qualidade em
                                     simples de integrar.    português.

  Chroma                             Integração com          Avaliar requisitos de
                                     LangChain e             produção e
                                     persistência local      distribuição.
                                     adequada ao MVP.

  Recuperação de três fragmentos     Limita contexto e       Comparar valores de `k`
                                     consumo de tokens.      com perguntas de
                                                             referência.

  Duas rondas de correção            Controla custo, tempo e Avaliar se o limite é
                                     chamadas ao LLM.        suficiente nos casos
                                                             reais.
  ----------------------------------------------------------------------------------

## 14. Próximas prioridades

1.  Consolidar a gestão de versões e a remoção de fragmentos obsoletos.
2.  Avaliar a recuperação com perguntas de referência e diferentes
    valores de `k`.
3.  Avaliar embeddings adequados aos documentos em português.
4.  Criar casos de teste para fidelidade, precisão, clareza e qualidade
    pedagógica.
5.  Avaliar a integração de tutoriais no ciclo de revisão.
6.  Implementar e testar a persistência de documentos e pacotes na OCI
    Object Storage.
7.  Validar a integração end-to-end entre AI Stack, backend e interface.
8.  Preparar cenários distintos para demonstração.

A prioridade é consolidar a fiabilidade do fluxo existente antes de
acrescentar complexidade arquitetural.

## 15. Princípio de desenvolvimento

A AI Stack deve evoluir com base em funcionalidades verificáveis,
contratos de dados explícitos e decisões técnicas justificadas.

O objetivo não é apenas gerar conteúdo com um LLM, mas construir um
fluxo que recupere conhecimento relevante, produza materiais
estruturados, valide resultados, identifique problemas, corrija o que
for possível e encaminhe casos não resolvidos para revisão humana.

------------------------------------------------------------------------

**NovaMente AI Stack --- recuperação de conhecimento, geração educativa
e revisão inteligente.**
