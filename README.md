# G10_BRASIL_equipo16_NovaMente
Sistema Inteligente de Adaptação e Geração de Conteúdo Educacional.

# O que é o NovaMente?

O NovaMente é uma plataforma que recebe documentação técnica em PDF, Markdown ou texto simples e a transforma automaticamente em material educacional adaptado ao perfil do destinatário, ao contexto temático e ao nível de profundidade exigido.

O sistema combina recuperação aumentada por geração (RAG), busca vetorial e geração assistida por modelos de linguagem para trabalhar sempre a partir do documento original.

O objetivo é reduzir o tempo necessário para converter documentação técnica complexa em material de estudo, mantendo dois princípios centrais:

* fidelidade à fonte, utilizando como contexto os fragmentos recuperados do documento original;
* adaptação pedagógica, ajustando a linguagem, o nível de profundidade e a apresentação ao perfil solicitado.

O escopo funcional das features extras concentra-se em dois formatos educacionais:

* Quiz interativo, com opções, resposta correta e justificativa;
* Flashcards, com conceito ou pergunta e sua explicação correspondente.

Outros formatos contemplados pelo produto, como tutoriais e resumos, fazem parte de iterações posteriores.

# Estrutura deste repo

```bash
.
├── ai_stack # raiz  da stack de AI incluindo dados de treinamento e modelos
├── backend # raiz da stack de backend
├── docs # raiz de toda a documentacao deste projeto
│   └── enunciado
│       └── Projeto1NovaMente.pdf
├── frontend # raiz da stack de frontend
├── LICENSE
└── README.md # este arquivo .
```

# Boas práticas de segurança
* Não se controlam versões de credenciais, tokens, chaves privadas nem segredos.
* Os arquivos `.env` de execução permanecem fora do Git.
* As configurações públicas são documentadas por meio do arquivo `.env.example`.
* O OCI Object Storage utiliza um bucket privado.
* O acesso a partir do backend utiliza identidade técnica e chaves de assinatura de API.
* As chaves privadas permanecem fora do repositório e das imagens do Docker.
* Os serviços internos não são expostos publicamente quando não for necessário.
* Os dados utilizados para avaliação são públicos ou preparados especificamente para o hackathon.
