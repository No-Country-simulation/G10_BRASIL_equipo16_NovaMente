Criar uma solução inteligente capaz de ingerir documentações técnicas, manuais de software, artigos ou bases de conhecimento e transformá-los automaticamente em conteúdos educacionais personalizados e estruturados de acordo com o perfil do destinatário, a indústria de aplicação e o formato pedagógico de saída escolhido. 

A aplicação deve receber materiais técnicos nos formatos suportados (arquivos PDF, Markdown ou textos brutos) e permitir a parametrização dos seguintes critérios: 

* Perfil do Destinatário: ex.: Iniciante / Transição de Carreira, Desenvolvedor Júnior / Pleno, Líder Técnico / Arquiteto, Gestor / Executivo (Não Técnico). 
* Formato Pedagógico de Saída: ex.: Guia Prático Passo a Passo (Tutorial), Flashcards de Memorização, Quiz Interativo com Justificativas, Resumo Executivo (TL;DR), Roteiro de Aula / Vídeo. 
* Nicho / Contexto de Aplicação: ex.: Fintech, Saúde, E-commerce, Geral. 

A inteligência da aplicação deverá: 

1. Extrair e indexar o conteúdo técnico utilizando técnicas de **RAG** (com segmentação em chunks e embeddings vetoriais) para fundamentar as respostas; 
2. Orquestrar um fluxo de agentes ou cadeias de prompts utilizando **LLMs de escolha da equipe** (Google Gemini, OpenAI ChatGPT/GPT-4o, Anthropic Claude, Grok, Ollama ou equivalentes) para reescrever, exemplificar e estruturar o conteúdo no nível de profundidade e tom adequados; 
3. Avaliar a coerência didática e gerar metadados de aprendizado (conceitos-chave, pré-requisitos, tempo estimado de estudo). 

Os resultados deverão ser disponibilizados em formato JSON estruturado para integração com sistemas externos, acompanhados de uma interface interativa (ex.: Streamlit ou Gradio). A persistência dos documentos e dos pacotes de conteúdo gerados deve utilizar obrigatoriamente o **OCI Object 
Storage** dentro da camada **Always Free da OCI**. 

A solução deve permitir: 

* **Ingerir documentos técnicos densos** sem necessidade de pré-processamento manual; 
* **Personalizar a linguagem e a didática** instantaneamente para diferentes públicos; 
* **Gerar múltiplos formatos de estudo** (quizzes, flashcards, tutoriais, resumos) com poucos cliques; 
* **Garantir confiabilidade**, assegurando que os conteúdos gerados não alucinem e reflitam fielmente 
o material original; 
* **Reduzir o tempo de produção de conteúdo** de semanas para minutos. 

Desenvolver um MVP (Mínimo Produto Viável) funcional capaz de: 

1. Ingerir e processar documentos técnicos de entrada (arquivos PDF, Markdown ou texto); 
2. Implementar uma pipeline de RAG com geração e busca de embeddings para ancorar as respostas na documentação fornecida; 
3. Orquestrar prompts e fluxos inteligentes utilizando LLMs (Google Gemini, OpenAI, Claude ou outros modelos via API/local) para adaptar o conteúdo ao perfil e formato requisitados; 
4. Gerar saídas em formato estruturado (JSON) contendo o conteúdo adaptado, termos-chave e avaliação pedagógica; 
5. Disponibilizar uma interface amigável (Streamlit / Gradio) ou API REST funcional; 
6. Integrar a solução obrigatoriamente com o OCI Object Storage (camada Always Free) para armazenar os documentos e os conteúdos gerados. 

### Resultados esperados 

#### 1. IA Generativa, RAG & Agentes 

Notebook ou módulos contendo: 

* Ingestão e extração de texto de documentos técnicos (ex.: biblioteca PyPDF ou leitores Markdown); 
* Pipeline de RAG: segmentação do texto (chunking), geração de embeddings e armazenamento em Vector Store (ex.: Chroma, FAISS ou similar); 
* Criação e otimização de prompts estruturados com técnicas de few-shot e role prompting; 
* Cadeia de orquestração (LangChain) ou Grafo de Decisão (LangGraph) para planejar, redigir e revisar o conteúdo gerado; 
* Mecanismo de verificação de fidelidade ao documento de origem para mitigar alucinações. 

#### 2. Back-End, Automação & Interface 

Aplicação funcional (Streamlit, Gradio, FastAPI, Flask ou equivalente) contendo: 

* Endpoint ou interface para upload do documento técnico e seleção dos parâmetros (perfil, formato, nicho); 
* Orquestração do fluxo de geração; 
* Validação de schemas de entrada e saída com tipagem estrita; 
* Tratamento de exceções e mensagens de erro amigáveis. 

#### 3. Oracle Cloud Infrastructure (OCI) — Camada Always Free 

* **Requisito Obrigatório (MVP): OCI Object Storage** — Criação de Bucket Always Free para persistir os documentos técnicos originais enviados e os arquivos JSON de conteúdo educacional adaptado gerados pelo sistema; 
* **Recurso Opcional / Diferencial: OCI Compute Instance ("Deploy Completo em Nuvem")** — Hospedagem da aplicação (Streamlit/Gradio ou API) em máquina virtual Always Free na OCI; 
* **Aviso Importante ONE**: Como o programa ONE é uma iniciativa social 100% gratuita para os alunos, deve-se utilizar estritamente a camada Always Free da OCI, evitando configurações que possam gerar custos monetários. 

#### 4. Documentação & Demonstração 

* Repositório Git estruturado com commits claros e colaborativos; 
* Arquivo README.md detalhado com arquitetura da solução, diagrama do fluxo RAG/Agentes e guia de instalação; 
* Demonstração prática apresentando pelo menos três cenários distintos de adaptação para um mesmo documento técnico. 

### Funcionalidades obrigatórias (MVP) 

#### Endpoint / Ação Principal: Adaptação de Conteúdo Educacional 

A aplicação deve expor uma interface ou endpoint capaz de receber o material técnico e os parâmetros de personalização, processá-lo pelo pipeline RAG + LLM e retornar o pacote educativo completo. 

Exemplo de Requisição (Entrada): 

```json
{ 
  "documento_titulo": "Introducao a Arquitetura de Redes VCN na OCI", 
  "documento_conteudo": "A Virtual Cloud Network (VCN) e uma rede privada e personalizavel configurada na Oracle Cloud Infrastructure. Semelhante a uma rede de data center tradicional, a VCN oferece controle total sobre seu ambiente de rede, incluindo sub-redes publicas e privadas, tabelas de roteamento, Internet Gateways, NAT Gateways e Security Lists para controle de trafego via regras de entrada (ingress) e saida (egress).", 
  "perfil_destinatario": "Iniciante", 
  "formato_saida": "Flashcards", 
  "nicho_setor": "Geral", 
  "nivel_detalhe": "Didatico" 
}
```

Exemplo de Resposta (Saída Estruturada):

```json
{ 
  "status": "sucesso", 
  "metadados": { 
    "perfil_aplicado": "Iniciante", 
    "formato_gerado": "Flashcards", 
    "tempo_estimado_estudo_minutos": 5, 
    "conceitos_chave": ["VCN", "Sub-redes", "Internet Gateway", "Security Lists"] 
  }, 
  "conteudo_adaptado": { 
    "titulo": "Dominando Redes na Nuvem (VCN) do Zero", 
    "introducao_contextualizada": "Imagine a VCN como o seu proprio bairro particular e seguro dentro da nuvem da Oracle, onde voce decide quem entra e quem sai.", 
    "itens": [
        { 
        "frente": "O que e uma VCN na Oracle Cloud?", 
        "verso": "E a sua rede virtual privada e personalizada dentro da nuvem da Oracle, funcionando como a infraestrutura de rede da sua empresa.", 
        "dica_didatica": "Pense nela como o terreno cercado onde seus servidores moram." 
      }, 
      { 
        "frente": "Para que servem as Security Lists (Listas de Seguranca)?", 
        "verso": "Sao como porteiros virtuais com listas de regras que definem exatamente que tipo de trafego de dados pode entrar ou sair da sua rede.", 
        "dica_didatica": "Regras de entrada (ingress) e regras de saida (egress)." 
      } 
    ] 
  }, 
  "avaliacao_qualidade": { 
    "ancoragem_fonte_score": 0.98, 
    "clareza_pedagogica": "Alta", 
    "observacoes": "Linguagem ajustada com analogias para publico iniciante, sem jargoes excessivos." 
  }, 
  "armazenamento_oci": { 
    "bucket": "novamente-conteudos-educativos", 
    "objeto_id": "conteudo-vcn-iniciante-flashcards-001.json", 
    "status_upload": "concluido" 
  } 
}
```
