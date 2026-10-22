# Guia de Power BI: do Power Query ao DAX avançado (PL-300)

Documentação de estudo baseada nas fontes da Microsoft, SQLBI, DAX Guide e Kimball Group, organizada em níveis, do iniciante ao avançado.

## Como usar este guia

O conteúdo segue a ordem natural de um projeto de BI: **preparar os dados → modelar → calcular → otimizar**. Cada nível apresenta o conceito, as ferramentas, para que serve, o que faz e o resultado esperado, e indica qual dos links de referência aprofundar.

| Nível | Tema | Pergunta que responde | Fontes principais |
| --- | --- | --- | --- |
| 0 | Visão geral e exame PL-300 | O que é e aonde quero chegar? | Página do PL-300 |
| 1 | Power Query e linguagem M | Como trago e limpo os dados? | Docs Power Query, Referência M |
| 2 | Query folding e consultas nativas | Como deixo a carga rápida? | Query folding, Native query |
| 3 | Modelagem dimensional e relacionamentos | Como organizo as tabelas? | Kimball, docs de relacionamentos, diretrizes |
| 4 | DAX essencial | Como crio cálculos? | Referência DAX, DAX Guide |
| 5 | DAX intermediário: CALCULATE e tempo | Como controlo o contexto? | CALCULATE, Time intelligence |
| 6 | Avançado: VertiPaq e desempenho | Por que fica lento e como corrigir? | SQLBI |

---

## Nível 0: Visão geral

### O que é o Power BI

O Power BI é a plataforma de análise de dados da Microsoft. Ele transforma dados espalhados (planilhas, bancos, APIs) em modelos organizados e relatórios interativos.

### Ferramentas do ecossistema

- **Power BI Desktop:** aplicativo gratuito onde você constrói o projeto (conectar, transformar, modelar, visualizar).
- **Power Query:** editor de transformação de dados (a etapa de ETL).
- **Modelo semântico:** tabelas, relacionamentos e medidas que dão significado aos dados.
- **DAX:** linguagem de fórmulas para criar cálculos no modelo.
- **Serviço Power BI (nuvem):** onde se publica, compartilha, agenda atualizações e aplica segurança.

### Fluxo de trabalho

1. **Obter dados** de uma ou mais fontes.
2. **Transformar** (limpar, tipar, combinar) no Power Query.
3. **Modelar** (relacionar tabelas, criar medidas).
4. **Visualizar** (gráficos, matrizes, filtros).
5. **Publicar e gerenciar** (atualização, segurança, workspaces).

### O exame PL-300 (Microsoft Power BI Data Analyst)

A página do exame no Microsoft Learn traz o **outline de habilidades** (o que é cobrado), a duração, os caminhos de estudo gratuitos e a prática oficial. As quatro grandes áreas avaliadas são:

1. Preparar os dados (Power Query, fontes, limpeza, perfilamento).
2. Modelar os dados (relacionamentos, esquema estrela, DAX, desempenho).
3. Visualizar e analisar os dados (relatórios, filtros, interações, insights).
4. Implantar e manter ativos (workspaces, atualização, segurança em nível de linha).

> Os pesos percentuais e itens do outline são atualizados periodicamente pela Microsoft. Confira sempre a versão vigente na página do exame antes de planejar o estudo.

**Resultado do nível 0:** você entende o mapa completo e sabe que este guia cobre principalmente as áreas 1 e 2, que são a base técnica do exame.

---

## Nível 1: Power Query e linguagem M (nível iniciante)

### O que é

O **Power Query** é o mecanismo de conexão e transformação de dados usado no Power BI, Excel, Dataflows e outros produtos. Cada ação que você faz na interface vira um **passo aplicado** (Applied Step), registrado como código na **linguagem M**.

### Para que serve

- Conectar a dezenas de fontes (Excel, CSV, SQL Server, web, APIs, SharePoint etc.).
- Limpar e padronizar: remover colunas, corrigir tipos, tratar nulos, dividir texto.
- Combinar: **mesclar** consultas (equivale a JOIN) e **acrescentar** consultas (equivale a UNION).
- Reutilizar a receita: ao atualizar, todos os passos rodam de novo automaticamente.

### Principais operações

| Operação | O que faz | Equivalente |
| --- | --- | --- |
| Remover/escolher colunas | Reduz o volume | SELECT |
| Filtrar linhas | Mantém só o necessário | WHERE |
| Alterar tipo | Define texto, número, data | CAST |
| Agrupar por | Resume dados | GROUP BY |
| Mesclar consultas | Une tabelas por chave | JOIN |
| Acrescentar consultas | Empilha tabelas | UNION |
| Dinamizar/Remover dinamização | Gira colunas e linhas | PIVOT/UNPIVOT |
| Coluna condicional | Regra if/else | CASE WHEN |

### Boas práticas iniciais

- Defina o **tipo de dados correto** cedo. Isso evita erros e melhora a compressão.
- Remova colunas desnecessárias o quanto antes.
- Dê nomes claros às consultas e aos passos.
- Use o perfilamento de colunas (qualidade, distribuição, perfil) para encontrar erros e valores vazios.
- Desmarque **"Habilitar carga"** em consultas apenas intermediárias.

### A linguagem M (nível iniciante para intermediário)

M é uma linguagem **funcional**, de **maiúsculas e minúsculas diferenciadas** (case-sensitive). Todo script tem a estrutura `let ... in`:

```
let
    Fonte = Csv.Document(File.Contents("C:\dados\vendas.csv"), [Delimiter=","]),
    Cabecalho = Table.PromoteHeaders(Fonte),
    Tipado = Table.TransformColumnTypes(Cabecalho, {{"Valor", type number}, {"Data", type date}}),
    Filtrado = Table.SelectRows(Tipado, each [Valor] > 0)
in
    Filtrado
```

Cada linha dentro do `let` é um passo que usa o resultado do anterior. O que vem depois de `in` é o resultado final.

**Tipos e estruturas essenciais:**

- **Valores primitivos:** `text`, `number`, `date`, `datetime`, `logical`, `null`.
- **Lista** `{1, 2, 3}`: sequência de valores.
- **Registro** `[Nome="Ana", Idade=30]`: conjunto de campos nomeados.
- **Tabela:** linhas e colunas (a estrutura principal do Power Query).
- **Função:** `(x) => x + 1`. O atalho `each` equivale a `(_) =>`.

A **Referência da linguagem M** documenta todas as funções por família: `Table.*`, `List.*`, `Text.*`, `Date.*`, `Record.*`, `Number.*`, `Json.*` e outras, além da especificação da linguagem (operadores, tratamento de erros com `try ... otherwise`, funções personalizadas).

**Resultado do nível 1:** você consegue conectar, limpar e combinar dados e ler o código M gerado pela interface.

---

## Nível 2: Query folding e consultas nativas (intermediário)

### O que é o query folding

É a capacidade do Power Query de **traduzir seus passos em uma única consulta na linguagem da fonte** (por exemplo, SQL) e deixar o banco fazer o trabalho pesado. Em vez de baixar milhões de linhas e filtrar localmente, o filtro é executado no servidor e só o resultado chega ao Power BI.

### Por que importa

- **Menos dados trafegados** e menor tempo de atualização.
- Aproveita índices e o poder do servidor.
- É essencial para atualização incremental e para modelos grandes.

### Como verificar

- Clique com o botão direito em um passo aplicado e veja se **"Exibir Consulta Nativa"** está habilitado. Se estiver, o passo foi dobrado.
- Se estiver desabilitado, o folding foi quebrado naquele passo ou antes dele.
- O **Diagnóstico de Consulta** e o plano de consulta ajudam a investigar.

### O que costuma quebrar o folding

- Funções de M sem equivalente na fonte (algumas funções de texto e data, colunas de índice em certos conectores).
- Mesclas entre fontes diferentes.
- Funções personalizadas aplicadas linha a linha.
- `Table.Buffer` e outras operações que forçam o processamento local.
- Fontes que não suportam folding (CSV, Excel, planilhas em geral).

**Regra prática:** coloque os passos que **dobram** (filtros, escolha de colunas, agrupamentos, mesclas simples) **primeiro**, e os que quebram o folding **por último**.

### Importar dados de banco com consulta nativa

É possível, ao conectar a um banco, informar uma **instrução SQL escrita à mão** (em *Opções avançadas → Instrução SQL*). Também existe a função `Value.NativeQuery` no M.

**Quando usar:** consultas complexas já prontas, procedures, hints ou funções específicas do banco.

**Pontos de atenção:**

- O Power BI pede uma **aprovação de consulta nativa** (segurança) na primeira execução.
- Dependendo do conector, **passos posteriores à consulta nativa podem não dobrar**. Em alguns conectores o folding continua; em outros, não. Teste com "Exibir Consulta Nativa".
- Dê preferência a **views** no banco quando possível: ficam versionadas, reutilizáveis e mantêm o folding.
- Parametrize para evitar SQL injection e facilitar manutenção.

**Resultado do nível 2:** você sabe medir e proteger o desempenho da carga e decidir entre interface, SQL nativo ou view.

---

## Nível 3: Modelagem de dados (intermediário)

### Por que modelar

Um bom modelo faz os cálculos serem **simples, rápidos e corretos**. Um modelo ruim exige DAX complicado e produz números errados.

### Modelagem dimensional (Kimball)

O Kimball Group estabeleceu os conceitos-base:

- **Tabela fato:** registra eventos mensuráveis (vendas, pedidos, cliques). Contém **métricas numéricas** e chaves para as dimensões.
- **Tabela dimensão:** descreve o contexto (cliente, produto, data, loja). Contém atributos usados para filtrar e agrupar.
- **Granularidade (grain):** o que uma linha da fato representa (ex.: uma linha por item de pedido). **Defina a granularidade primeiro.**
- **Esquema estrela:** uma fato no centro e dimensões ao redor, relacionadas diretamente. É o desenho recomendado para o Power BI.
- **Esquema floco de neve:** dimensões normalizadas em várias tabelas. Funciona, mas costuma ser menos eficiente e mais difícil de usar.

Processo clássico de quatro passos: **escolher o processo de negócio → declarar a granularidade → identificar as dimensões → identificar os fatos.**

**Técnicas adicionais frequentes:**

| Técnica | Ideia |
| --- | --- |
| Dimensão conforme | A mesma dimensão (ex.: Data) compartilhada por várias fatos |
| Dimensão role-playing | Uma dimensão usada em papéis diferentes (Data do pedido, Data de envio) |
| Dimensão degenerada | Identificador (nº do pedido) que fica na própria fato |
| Dimensão lixo (junk) | Agrupa flags e indicadores de baixa cardinalidade |
| Chave substituta (surrogate) | Chave artificial, estável, independente do sistema de origem |
| Dimensão de variação lenta (SCD) | Trata mudanças históricas em atributos (tipos 0, 1, 2, 3...) |
| Fato sem fato (factless) | Registra eventos sem métrica (presença, elegibilidade) |

### Relacionamentos no Power BI Desktop

Um relacionamento liga duas tabelas por uma coluna e define **como os filtros se propagam**.

**Cardinalidade:**

- **Um para muitos (1:\*):** o mais comum e desejado (dimensão → fato).
- **Um para um (1:1):** raro; geralmente indica que as tabelas podem ser unificadas.
- **Muitos para muitos (*:*):** exige cuidado (veja abaixo).

**Direção do filtro cruzado:**

- **Única:** o filtro vai da dimensão para a fato (padrão recomendado).
- **Ambas (bidirecional):** o filtro vai nos dois sentidos.

**Outros conceitos:** relacionamento **ativo/inativo**, **integridade referencial**, relacionamentos de **tabelas de fonte diferente** (limitados) e a cardinalidade dos lados do relacionamento.

### Diretrizes oficiais

**Tabelas de datas**

- Crie uma **tabela Calendário dedicada**, com datas **contíguas e sem lacunas**, cobrindo todo o período dos dados.
- **Marque como tabela de datas** no modelo (isso habilita a inteligência de tempo corretamente).
- Relacione a coluna de data da fato com a coluna de data da dimensão.
- Considere **desabilitar a data/hora automática**, que cria tabelas ocultas para cada coluna de data e aumenta o tamanho do modelo.
- Inclua colunas úteis: ano, trimestre, mês, nome do mês, número do mês para ordenação, dia da semana.

**Relacionamentos ativos e inativos**

- Entre duas tabelas só pode haver **um relacionamento ativo**. Os demais ficam **inativos**.
- Use o inativo sob demanda com `USERELATIONSHIP` dentro de `CALCULATE`.
- Caso típico: a fato tem *Data do pedido* e *Data de envio*. Um relacionamento fica ativo; a medida de envio ativa o outro.
- Alternativa: criar **várias tabelas de data** (role-playing) quando se quer filtrar por ambas ao mesmo tempo.

**Filtragem bidirecional**

- É útil em cenários específicos, mas **pode gerar ambiguidade, resultados inesperados e queda de desempenho**.
- Prefira manter a direção **única** e, quando precisar do efeito bidirecional, aplique-o **por medida** (`CROSSFILTER`, `TREATAS`) ou use a opção de segurança em nível de linha com cuidado.

**Relacionamentos muitos-para-muitos**

- Podem ocorrer quando nenhuma das colunas é única.
- Opções: (1) **tabela ponte** (bridge) com dois relacionamentos 1:\*, que é a abordagem mais clara; (2) cardinalidade *:* nativa; (3) relacionar em granularidade diferente (por exemplo, metas por categoria × vendas por produto).
- Entenda a **granularidade** de cada lado antes de escolher.

**Resultado do nível 3:** você desenha um esquema estrela, escolhe a cardinalidade e a direção corretas e prepara uma tabela de datas pronta para cálculos de tempo.

---

## Nível 4: DAX essencial (intermediário)

### O que é o DAX

**DAX (Data Analysis Expressions)** é a linguagem de fórmulas do Power BI, do Analysis Services e do Power Pivot. Ela cria **cálculos que reagem aos filtros** do relatório.

### Três lugares para usar DAX

| Item | Quando é calculado | Onde fica | Uso típico |
| --- | --- | --- | --- |
| **Medida** | Em tempo de consulta, a cada interação | Não ocupa linhas; é uma fórmula | Totais, razões, KPIs |
| **Coluna calculada** | Na atualização do modelo | Armazenada na tabela (usa memória) | Categorias, chaves, texto de ordenação |
| **Tabela calculada** | Na atualização do modelo | Nova tabela no modelo | Calendário, tabelas auxiliares |

**Regra de ouro:** para valores agregados use **medidas**. Use coluna calculada só quando precisar de um valor por linha para filtrar, agrupar ou ordenar.

### Exemplos básicos

```
Total Vendas = SUM(Vendas[Valor])

Qtde Pedidos = DISTINCTCOUNT(Vendas[IdPedido])

Ticket Médio = DIVIDE([Total Vendas], [Qtde Pedidos])

Lucro = [Total Vendas] - [Total Custo]
```

`DIVIDE` é preferível a `/` porque trata a divisão por zero.

### Famílias de funções (Referência DAX)

- **Agregação:** `SUM`, `AVERAGE`, `MIN`, `MAX`, `COUNT`, `DISTINCTCOUNT`.
- **Iteradoras (terminam em X):** `SUMX`, `AVERAGEX`, `MAXX`, `RANKX`. Percorrem linha a linha, avaliam uma expressão e agregam.
- **Lógicas:** `IF`, `SWITCH`, `AND`, `OR`, `COALESCE`.
- **Texto, data e informação:** `FORMAT`, `CONCATENATE`, `LEFT`, `YEAR`, `ISBLANK`.
- **Filtro:** `FILTER`, `ALL`, `VALUES`, `SELECTEDVALUE`, `RELATED`, `RELATEDTABLE`.
- **Tabela:** `SUMMARIZE`, `ADDCOLUMNS`, `TOPN`, `CALENDAR`, `CALENDARAUTO`.

### Variáveis

`VAR` e `RETURN` tornam a fórmula legível e podem melhorar o desempenho, pois o valor é calculado uma vez:

```
Margem % =
VAR Receita = [Total Vendas]
VAR Custo = [Total Custo]
RETURN DIVIDE(Receita - Custo, Receita)
```

### Os dois contextos (o coração do DAX)

- **Contexto de filtro:** o conjunto de filtros ativos vindos de segmentações, linhas e colunas do visual, e filtros do relatório. Define **quais linhas** entram no cálculo.
- **Contexto de linha:** a linha atual durante uma iteração (colunas calculadas e funções X). Sozinho **não filtra** outras tabelas.
- **Transição de contexto:** `CALCULATE` converte o contexto de linha em contexto de filtro. É a origem da maioria das dúvidas e dos "mistérios" do DAX.

### DAX Guide

O **dax.guide** é um dicionário com todas as funções, sintaxe, parâmetros, exemplos, e a indicação de **onde a função é suportada** (Power BI, SSAS, Excel). Use-o como consulta rápida do dia a dia, junto com a documentação oficial.

**Resultado do nível 4:** você cria medidas corretas, entende por que o valor muda conforme o visual e usa variáveis para escrever código limpo.

---

## Nível 5: CALCULATE e inteligência de tempo (intermediário a avançado)

### A função CALCULATE

É a função mais importante do DAX. Ela **avalia uma expressão em um contexto de filtro modificado**.

```
CALCULATE( <expressão>, <filtro1>, <filtro2>, ... )
```

**O que ela faz:**

1. Pega o contexto de filtro atual.
2. Aplica os filtros informados (**adicionando, substituindo ou removendo** filtros).
3. Avalia a expressão nesse novo contexto.

```
Vendas Brasil = CALCULATE([Total Vendas], Clientes[País] = "Brasil")

Vendas Total Geral = CALCULATE([Total Vendas], REMOVEFILTERS(Produtos))

% do Total =
DIVIDE([Total Vendas], CALCULATE([Total Vendas], ALL(Produtos)))
```

**Modificadores comuns:**

| Função | Efeito |
| --- | --- |
| `ALL` / `REMOVEFILTERS` | Remove filtros de tabela(s) ou coluna(s) |
| `ALLEXCEPT` | Remove todos, exceto os indicados |
| `ALLSELECTED` | Remove filtros do visual, mantém as seleções externas |
| `KEEPFILTERS` | Soma o filtro ao existente em vez de substituir |
| `USERELATIONSHIP` | Ativa um relacionamento inativo na medida |
| `CROSSFILTER` | Altera a direção do filtro na medida |
| `TREATAS` | Aplica valores de uma tabela como filtro em outra coluna |

**Pontos importantes:**

- Um filtro booleano simples (`Tabela[Coluna] = valor`) é convertido internamente em um filtro sobre a coluna e **substitui** filtros existentes **nessa mesma coluna**.
- A ordem de avaliação é: filtros externos → modificadores/filtros de `CALCULATE` → transição de contexto.
- Use `FILTER` quando a condição envolver **várias colunas ou medidas**, mas prefira filtros booleanos simples quando possível (são mais eficientes).

### Funções de inteligência de tempo

Permitem comparar períodos: acumulado no ano, mesmo período do ano anterior, últimos 12 meses etc.

**Requisitos:** uma **tabela de datas** contígua, marcada como tabela de datas e relacionada à fato.

| Necessidade | Função | Exemplo |
| --- | --- | --- |
| Acumulado no ano | `TOTALYTD`, `DATESYTD` | `TOTALYTD([Total Vendas], Calendario[Data])` |
| Acumulado no mês/trimestre | `TOTALMTD`, `TOTALQTD` | `TOTALMTD([Total Vendas], Calendario[Data])` |
| Mesmo período do ano anterior | `SAMEPERIODLASTYEAR` | `CALCULATE([Total Vendas], SAMEPERIODLASTYEAR(Calendario[Data]))` |
| Deslocar períodos | `DATEADD`, `PARALLELPERIOD` | `CALCULATE([Total Vendas], DATEADD(Calendario[Data], -1, MONTH))` |
| Janela móvel | `DATESINPERIOD` | Últimos 12 meses |
| Intervalo arbitrário | `DATESBETWEEN` | Entre duas datas |
| Primeiro/último dia | `STARTOFMONTH`, `ENDOFYEAR`, `FIRSTDATE`, `LASTDATE` | Saldos de fechamento |
| Saldo de abertura/fechamento | `OPENINGBALANCEMONTH`, `CLOSINGBALANCEYEAR` | Estoque, caixa |

**Exemplo de variação anual:**

```
Vendas Ano Anterior =
CALCULATE([Total Vendas], SAMEPERIODLASTYEAR(Calendario[Data]))

Variação % YoY =
DIVIDE([Total Vendas] - [Vendas Ano Anterior], [Vendas Ano Anterior])
```

**Cuidados:** use a coluna de data da **tabela Calendário**, não da fato; garanta que a tabela cubra anos completos; e lembre que as funções retornam **tabelas de datas** usadas como filtro dentro de `CALCULATE`.

**Resultado do nível 5:** você controla filtros com precisão e entrega indicadores de comparação temporal confiáveis.

---

## Nível 6: Avançado, VertiPaq e desempenho

### O SQLBI como fonte avançada

O **SQLBI** (Marco Russo e Alberto Ferrari) reúne artigos, vídeos, ferramentas e livros de referência sobre DAX, modelagem e desempenho. É o material de aprofundamento mais usado pela comunidade. Entre os temas centrais:

- Contexto de filtro, contexto de linha e transição de contexto em detalhes.
- Tabelas expandidas e propagação de filtros.
- Linhagem de dados (data lineage) e `TREATAS`.
- Padrões de DAX (comparação de períodos, ranking, ABC, semiaditividade, cálculos dinâmicos).
- Grupos de cálculo (calculation groups) para evitar duplicar medidas.

### O mecanismo VertiPaq

O **VertiPaq** é o motor de armazenamento em memória, **colunar e comprimido**, usado no modo Importar.

**Conceitos-chave:**

- **Armazenamento colunar:** cada coluna é guardada separadamente, o que acelera agregações.
- **Compressão:** codificação por dicionário, por valor e por repetição (RLE). **Quanto menor a cardinalidade (valores distintos) de uma coluna, melhor a compressão.**
- **Dois motores na consulta DAX:**
  - **Storage Engine (SE):** rápido, multi-thread, lê dados comprimidos.
  - **Formula Engine (FE):** single-thread, executa a lógica mais complexa do DAX.
  - Consultas rápidas deixam o máximo possível de trabalho no SE.

### Práticas de otimização do modelo

- Remova colunas não usadas e reduza a **cardinalidade** (por exemplo, separe data e hora em colunas distintas; arredonde decimais desnecessários).
- Prefira **inteiros** como chaves de relacionamento.
- Evite colunas calculadas pesadas quando uma medida resolve.
- Mantenha o esquema estrela e evite bidirecionalidade e *:* sem necessidade.
- Use agregações e atualização incremental em tabelas fato grandes.

### Práticas de otimização de DAX

- Use `VAR` para não recalcular a mesma expressão.
- Prefira filtros booleanos simples a `FILTER(tabela inteira)`.
- Evite iteradores aninhados sobre tabelas grandes.
- Use `DIVIDE`, `SELECTEDVALUE` e `COALESCE` em vez de lógica `IF` longa.
- Meça antes de otimizar.

### Ferramentas de análise

| Ferramenta | Para que serve |
| --- | --- |
| **Performance Analyzer** (Power BI Desktop) | Mostra o tempo de cada visual e a consulta DAX gerada |
| **DAX Studio** | Executa consultas, mostra plano de execução e tempos SE/FE |
| **VertiPaq Analyzer** | Mostra tamanho de tabelas, colunas e dicionários |
| **Tabular Editor** | Edita o modelo, cria grupos de cálculo e executa boas práticas |

**Resultado do nível 6:** você diagnostica lentidão, entende o porquê e reduz o tamanho e o tempo de consulta do modelo.

---

## Roteiro de estudo sugerido

1. **Semana 1:** Power Query (interface, tipos, mesclar e acrescentar) e leitura básica de M.
2. **Semana 2:** Query folding, consultas nativas e conexão com bancos.
3. **Semana 3:** Modelagem dimensional, esquema estrela, relacionamentos e tabela de datas.
4. **Semana 4:** DAX essencial: medidas, contextos, variáveis.
5. **Semana 5:** `CALCULATE`, inteligência de tempo e relacionamentos inativos.
6. **Semana 6:** Desempenho (VertiPaq, DAX Studio) e simulados do PL-300.

**Projeto prático:** monte um modelo de vendas com fato de pedidos, dimensões de produto, cliente e calendário. Crie as medidas Total, Ticket Médio, YTD, Ano Anterior e Variação %, e depois meça o tempo de atualização e o tamanho do modelo.

## Como cada link se encaixa

| Link | Nível | Uso |
| --- | --- | --- |
| Página do PL-300 | 0 | Define o que estudar e como praticar |
| Documentação do Power Query | 1 | Guia geral de conexão e transformação |
| Referência da linguagem M | 1 | Consulta de funções e sintaxe do M |
| Fundamentos de query folding | 2 | Desempenho na carga de dados |
| Importar dados de banco com consulta nativa | 2 | SQL escrito à mão e seus impactos |
| Técnicas Kimball | 3 | Base teórica da modelagem dimensional |
| Relacionamentos de modelo | 3 | Cardinalidade, direção, propagação de filtros |
| Diretrizes: tabelas de datas | 3 e 5 | Pré-requisito da inteligência de tempo |
| Diretrizes: ativos e inativos | 3 e 5 | Várias datas e `USERELATIONSHIP` |
| Diretrizes: bidirecional | 3 | Quando evitar e alternativas |
| Diretrizes: muitos-para-muitos | 3 | Tabela ponte e granularidades diferentes |
| Referência de funções DAX | 4 | Catálogo oficial |
| DAX Guide | 4 a 6 | Consulta rápida com exemplos |
| Função CALCULATE | 5 | Controle de contexto de filtro |
| Funções de inteligência de tempo | 5 | Comparações e acumulados |
| SQLBI | 6 | Aprofundamento em DAX e VertiPaq |

## Glossário rápido

- **ETL:** extrair, transformar e carregar dados.
- **Passo aplicado:** uma etapa registrada no Power Query.
- **Query folding:** tradução dos passos do M para a linguagem da fonte.
- **Fato / Dimensão:** tabela de eventos mensuráveis / tabela de contexto descritivo.
- **Granularidade:** o que uma linha da tabela representa.
- **Cardinalidade:** relação entre quantidades de valores únicos (1:\*, 1:1, *:*).
- **Medida:** cálculo dinâmico em DAX avaliado em tempo de consulta.
- **Contexto de filtro:** filtros ativos que definem quais linhas entram no cálculo.
- **Transição de contexto:** conversão de contexto de linha em filtro, feita por `CALCULATE`.
- **VertiPaq:** motor colunar em memória do modelo no modo Importar.
- **SE / FE:** Storage Engine / Formula Engine.

> As fontes são mantidas e atualizadas pelos seus autores. Confirme nos links originais as informações sujeitas a mudança, como o outline do exame, a disponibilidade de recursos e a sintaxe de funções novas.
