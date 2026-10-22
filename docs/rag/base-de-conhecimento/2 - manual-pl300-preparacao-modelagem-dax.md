---
titulo: "Preparação, Modelagem Dimensional e Cálculos DAX no Microsoft Power BI para a Certificação PL-300"
tipo: manual técnico de referência (fonte primária para ingestão em RAG educacional)
idioma: pt-BR
certificacao: PL-300 Microsoft Power BI Data Analyst
dominios_cobertos: Prepare os dados, Modele os dados
fonte_de_verdade: documentação oficial Microsoft Learn (links na seção 9)
---

# Preparação, Modelagem Dimensional e Cálculos DAX no Microsoft Power BI para a Certificação PL-300

Este manual cobre, em profundidade, o caminho completo que um dado percorre no Power BI: extração de um banco relacional transacional (PostgreSQL) com Power Query e linguagem M, reestruturação até a 3FN, transformação em modelo dimensional (esquema estrela) e consumo por medidas DAX. Cada seção inicia com um parágrafo de contexto autocontido e usa terminologia fixa, de modo que cada trecho possa ser recuperado isoladamente por um sistema de busca vetorial sem perder significado.

Convenções de nomenclatura usadas em todos os exemplos: o banco de origem é um ERP comercial fictício chamado `erp_comercial`, com as tabelas transacionais `cliente`, `pedido`, `item_pedido`, `produto` e `categoria`. O modelo analítico de destino tem a tabela fato `FatVendas` e as dimensões `DimData`, `DimCliente` e `DimProduto`.

Observação de validade: nomes de funções, parâmetros e comportamentos descritos aqui seguem a documentação oficial consultada em outubro de 2026. O outline de habilidades medidas do PL-300 é revisado periodicamente pela Microsoft; confira a versão vigente na página oficial do exame antes de fechar o cronograma de estudos.

---

## 1. Visão geral do pipeline analítico no Power BI

O Power BI organiza o trabalho em três camadas encadeadas. A camada de preparação (Power Query, linguagem M) extrai e transforma os dados antes da carga. A camada de modelo (motor VertiPaq, tabelas, colunas e relacionamentos) armazena os dados de forma colunar comprimida. A camada de cálculo (DAX) avalia expressões sobre o modelo em resposta às consultas geradas pelos visuais. Cada visual de um relatório gera uma consulta DAX enviada ao modelo semântico; por isso a qualidade do modelo determina diretamente desempenho, simplicidade das medidas e corretude dos resultados.

A regra de ouro para o exame e para a prática profissional é: transformações de forma e limpeza pertencem ao Power Query, relacionamentos e granularidade pertencem ao modelo, e agregações dinâmicas dependentes de contexto pertencem ao DAX. Colocar lógica na camada errada (por exemplo, calcular em DAX uma coluna que poderia ser resolvida na origem ou no Power Query) degrada compressão, tempo de atualização e legibilidade.

### 1.1 Papel de cada linguagem

| Camada | Linguagem | Momento de execução | Resultado persistido |
|---|---|---|---|
| Extração e transformação | M (Power Query) | Na atualização do modelo (refresh) | Tabelas carregadas e comprimidas |
| Colunas calculadas | DAX | Na atualização do modelo | Colunas materializadas na memória |
| Medidas | DAX | Em tempo de consulta, por célula de visual | Nada; avaliação sob demanda |
| Tabelas calculadas | DAX | Na atualização do modelo | Tabela materializada |

---

## 2. Extração de dados de PostgreSQL com Power Query

Esta seção descreve a conexão com um banco relacional transacional PostgreSQL, a escolha entre navegação por tabelas e consulta nativa, e o impacto no query folding. O conector `PostgreSQL.Database` exige que o provedor Npgsql compatível esteja instalado na máquina que executa o Power Query Desktop; no serviço, a conexão via gateway segue requisitos próprios. A documentação oficial do conector está na seção 9.

### 2.1 Conexão por navegação (recomendada quando possível)

A navegação cria um objeto de origem a partir do qual schemas e tabelas são acessados como campos de registro. Operações subsequentes (filtros, seleção de colunas, junções simples) são traduzidas para SQL pelo mecanismo de query folding, de modo que o processamento ocorre no servidor.

```m
let
    Origem = PostgreSQL.Database("srv-pg.exemplo.com:5432", "erp_comercial"),
    Pedido = Origem{[Schema = "public", Item = "pedido"]}[Data],
    Recentes = Table.SelectRows(Pedido, each [dt_pedido] >= #datetime(2024, 1, 1, 0, 0, 0)),
    Colunas = Table.SelectColumns(Recentes, {"id_pedido", "id_cliente", "dt_pedido", "vl_desconto"})
in
    Colunas
```

Se o filtro e a seleção de colunas dobrarem (fold), o servidor receberá um único `SELECT ... WHERE dt_pedido >= ...`. Para verificar, clique com o botão direito no passo aplicado e confira se a opção "Exibir Consulta Nativa" está habilitada. Se estiver desabilitada, o passo (ou algum anterior) quebrou o folding.

### 2.2 Consulta nativa com Value.NativeQuery

Consultas nativas executam SQL escrito pelo analista diretamente no PostgreSQL. São úteis quando a lógica depende de recursos do SQL do servidor (funções de janela, CTEs, `DISTINCT ON`) que o conector não traduz. Pela documentação oficial, o dobramento de consulta nativa está habilitado por padrão no conector PostgreSQL, mas não se aplica quando há parâmetros opcionais presentes em `Value.NativeQuery`. A assinatura é `Value.NativeQuery(target as any, query as text, optional parameters as any, optional options as nullable record)`.

```m
let
    Origem = PostgreSQL.Database("srv-pg.exemplo.com:5432", "erp_comercial"),
    ItensDetalhados = Value.NativeQuery(
        Origem,
        "SELECT i.id_pedido, i.id_produto, i.quantidade, i.preco_unitario,
                p.id_cliente, p.dt_pedido
           FROM public.item_pedido i
           JOIN public.pedido p ON p.id_pedido = i.id_pedido
          WHERE p.dt_pedido >= DATE '2024-01-01'",
        null,
        [EnableFolding = true]
    )
in
    ItensDetalhados
```

Pontos de atenção técnicos. Primeiro, com `EnableFolding = true`, o Power Query envolve o SQL nativo em uma subconsulta para dobrar passos posteriores; por isso o SQL não deve terminar com ponto e vírgula nem conter cláusulas que não possam ser subconsulta. Segundo, a documentação indica que um erro do tipo "não é possível dobrar sobre esta consulta nativa" aparece quando a consulta não suporta esse encapsulamento, e que um teste básico de diagnóstico é verificar se a mesma consulta falha quando envolvida por uma cláusula `limit 1`. Terceiro, consultas nativas dão ao Power BI permissão para executar SQL arbitrário; em ambientes corporativos, a aprovação de consulta nativa é solicitada na primeira execução e a conta de acesso deve ter privilégio apenas de leitura.

### 2.3 Boas práticas de extração

Selecione apenas colunas e linhas necessárias na origem; reduza cardinalidade antes de carregar; defina tipos explícitos o quanto antes (`Table.TransformColumnTypes`) para evitar inferência instável; use parâmetros do Power Query para servidor e banco, de modo que o mesmo arquivo funcione em desenvolvimento e produção; e desative a carga (Habilitar Carga desmarcado) de consultas intermediárias que servem apenas de estágio. A consulta de origem compartilhada deve ser referenciada (`Reference`) e não duplicada (`Duplicate`), pois referenciar reaproveita o mesmo plano de extração, enquanto duplicar cria uma consulta independente com sua própria execução contra o banco.

---

## 3. Atomicidade de atributos e normalização (1FN, 2FN, 3FN) em linguagem M

Esta seção mostra como usar o Editor do Power Query para garantir conformidade estrutural com as três primeiras formas normais sobre dados de origem que não as respeitam. Um esclarecimento conceitual é essencial: em modelagem analítica o destino final costuma ser desnormalizado (esquema estrela). A normalização no Power Query é um passo de saneamento estrutural, usado para eliminar redundâncias e anomalias antes de reagrupar as entidades em dimensões e fatos com granularidade definida. Normalizar e depois dimensionar é um caminho de duas etapas, e cada uma tem objetivo distinto.

### 3.1 Primeira Forma Normal (1FN): atomicidade e ausência de grupos repetitivos

Uma relação está na 1FN quando todos os atributos são atômicos (um único valor por célula) e não há grupos repetitivos de colunas. Violações típicas: listas delimitadas dentro de uma coluna, atributos compostos (endereço completo em um campo) e colunas repetidas numeradas (`telefone1`, `telefone2`, `telefone3`).

Caso 1, lista delimitada: a coluna `telefones` contém `"6199999-0001; 6188888-0002"`. A solução é dividir em lista, expandir para linhas e aparar espaços.

```m
let
    Fonte = Table.FromRecords({
        [id_cliente = 1, nome = "Ana",   telefones = "6199999-0001; 6188888-0002"],
        [id_cliente = 2, nome = "Bruno", telefones = "6177777-0003"]
    }),
    ComoLista = Table.TransformColumns(
        Fonte, {{"telefones", each Text.Split(_, ";"), type list}}),
    Expandido = Table.ExpandListColumn(ComoLista, "telefones"),
    Aparado = Table.TransformColumns(Expandido, {{"telefones", Text.Trim, type text}})
in
    Aparado
```

Caso 2, grupo repetitivo de colunas: `telefone1`, `telefone2`, `telefone3` viram uma única coluna por meio de despivotamento, descartando nulos.

```m
let
    Fonte = Table.FromRecords({
        [id_cliente = 1, nome = "Ana",   telefone1 = "6199999-0001", telefone2 = "6188888-0002", telefone3 = null],
        [id_cliente = 2, nome = "Bruno", telefone1 = "6177777-0003", telefone2 = null,          telefone3 = null]
    }),
    Despivotado = Table.UnpivotOtherColumns(
        Fonte, {"id_cliente", "nome"}, "origem_atributo", "telefone"),
    SemNulos = Table.SelectRows(Despivotado, each [telefone] <> null),
    Final = Table.RemoveColumns(SemNulos, {"origem_atributo"})
in
    Final
```

Caso 3, atributo composto: o campo `endereco` no formato `"Rua das Flores, 120 - Asa Sul - Brasília/DF"` é decomposto em componentes atômicos.

```m
let
    Fonte = Table.FromRecords({
        [id_cliente = 1, endereco = "Rua das Flores, 120 - Asa Sul - Brasília/DF"]
    }),
    PorTraco = Table.SplitColumn(
        Fonte, "endereco",
        Splitter.SplitTextByDelimiter(" - ", QuoteStyle.None),
        {"logradouro_num", "bairro", "cidade_uf"}),
    PorBarra = Table.SplitColumn(
        PorTraco, "cidade_uf",
        Splitter.SplitTextByDelimiter("/", QuoteStyle.None),
        {"cidade", "uf"}),
    PorVirgula = Table.SplitColumn(
        PorBarra, "logradouro_num",
        Splitter.SplitTextByDelimiter(", ", QuoteStyle.None),
        {"logradouro", "numero"}),
    Tipado = Table.TransformColumnTypes(PorVirgula, {{"numero", Int64.Type}})
in
    Tipado
```

### 3.2 Segunda Forma Normal (2FN): eliminação de dependências parciais

Uma relação está na 2FN quando está na 1FN e todo atributo não chave depende da chave primária inteira, não de parte dela. O problema só existe em chaves compostas. Exemplo: `item_pedido(id_pedido, id_produto, quantidade, nome_produto, preco_tabela)` tem chave composta `(id_pedido, id_produto)`, mas `nome_produto` e `preco_tabela` dependem apenas de `id_produto`. A decomposição extrai os atributos dependentes parciais para uma relação própria cuja chave é o determinante parcial.

Antes de decompor, valide empiricamente a dependência funcional. A função abaixo retorna as violações: valores do determinante que se associam a mais de um valor do dependente.

```m
// Consulta: fnVerificarDF
(t as table, determinante as list, dependente as text) as table =>
let
    Agrupado = Table.Group(
        t, determinante,
        {{"qtd_valores_distintos",
          each List.Count(List.Distinct(Table.Column(_, dependente))),
          Int64.Type}}),
    Violacoes = Table.SelectRows(Agrupado, each [qtd_valores_distintos] > 1)
in
    Violacoes
```

Se `fnVerificarDF(ItemPedido, {"id_produto"}, "nome_produto")` retornar zero linhas, a dependência `id_produto → nome_produto` é consistente nos dados atuais. Em seguida, aplique a decomposição.

```m
let
    ItemPedido = Origem_ItemPedido,   // consulta anterior com as 5 colunas
    ProdutoExtraido = Table.Distinct(
        Table.SelectColumns(ItemPedido, {"id_produto", "nome_produto", "preco_tabela"}),
        {"id_produto"}),
    ItemPedido2FN = Table.RemoveColumns(ItemPedido, {"nome_produto", "preco_tabela"})
in
    ItemPedido2FN   // a consulta ProdutoExtraido é mantida em outra consulta
```

Atenção: `Table.Distinct` com lista de colunas-chave mantém a primeira ocorrência por chave e descarta as demais silenciosamente. Se existirem conflitos de valores, esse passo mascara o defeito de qualidade. Por isso a validação com `fnVerificarDF` deve preceder a deduplicação.

### 3.3 Terceira Forma Normal (3FN): eliminação de dependências transitivas

Uma relação está na 3FN quando está na 2FN e nenhum atributo não chave depende de outro atributo não chave. Exemplo: `produto(id_produto, nome_produto, id_categoria, nome_categoria)`. Aqui `id_produto → id_categoria` e `id_categoria → nome_categoria`, portanto `nome_categoria` depende transitivamente de `id_produto`. A decomposição cria `categoria(id_categoria, nome_categoria)`.

```m
let
    Produto = Origem_Produto,
    Categoria = Table.Distinct(
        Table.SelectColumns(Produto, {"id_categoria", "nome_categoria"}),
        {"id_categoria"}),
    Produto3FN = Table.RemoveColumns(Produto, {"nome_categoria"})
in
    Produto3FN
```

### 3.4 Reagrupando para o modelo dimensional

Depois de saneado, o conjunto normalizado é reunido por junções para formar dimensões. A dimensão de produto absorve a categoria (desnormalização controlada) e recebe uma chave substituta (surrogate key).

```m
let
    Produto = Produto3FN,
    Categoria = CategoriaDistinta,
    Juntado = Table.NestedJoin(
        Produto, {"id_categoria"}, Categoria, {"id_categoria"},
        "cat", JoinKind.LeftOuter),
    Expandido = Table.ExpandTableColumn(Juntado, "cat", {"nome_categoria"}),
    ComSK = Table.AddIndexColumn(Expandido, "sk_produto", 1, 1, Int64.Type),
    Ordenado = Table.ReorderColumns(ComSK,
        {"sk_produto", "id_produto", "nome_produto", "nome_categoria"})
in
    Ordenado
```

Nota sobre chave substituta: o índice gerado no Power Query é recalculado a cada atualização e pode mudar se a ordem das linhas mudar. Para dimensões com histórico (SCD tipo 2) ou quando a chave precisa ser estável entre atualizações, gere a chave substituta no data warehouse; no Power Query, prefira usar a chave natural do sistema transacional como chave do relacionamento quando ela for única e estável.

### 3.5 Tipos, erros e perfilamento

Defina tipos com cultura explícita quando houver texto numérico: `Table.TransformColumnTypes(t, {{"preco", type number}}, "pt-BR")`. Trate erros de linha com `try ... otherwise` em colunas calculadas ou use `Table.RemoveRowsWithErrors` quando o descarte for aceitável e documentado. Habilite perfilamento de coluna baseado no conjunto de dados inteiro (e não apenas nas primeiras 1.000 linhas) ao diagnosticar qualidade: Exibição, Qualidade da Coluna, Distribuição da Coluna e Perfil da Coluna.

```m
let
    Fonte = Origem_ItemPedido,
    ComPrecoSeguro = Table.AddColumn(
        Fonte, "preco_num",
        each try Number.From([preco_unitario_texto]) otherwise null,
        type nullable number)
in
    ComPrecoSeguro
```

### 3.6 Query folding: o que quebra e como proteger

O folding é a tradução dos passos de M em uma única instrução SQL executada no servidor. Passos que usualmente dobram: seleção e remoção de colunas, filtros de linha, renomeações, junções entre consultas da mesma origem, agrupamentos simples, ordenação. Passos que usualmente quebram o folding: `Table.AddIndexColumn`, funções M personalizadas aplicadas por linha, `Table.Buffer`, `Table.UnpivotOtherColumns` em certos conectores, junções entre origens distintas, e transformações de texto sem equivalente SQL. Princípio operacional: coloque os passos dobráveis primeiro e os não dobráveis por último, de modo que o servidor reduza o volume antes de o mecanismo de mashup assumir.

---

## 4. Modelagem dimensional: do modelo relacional ao esquema estrela

Esta seção formaliza a transição de um modelo transacional normalizado (otimizado para escrita e integridade) para um modelo dimensional (otimizado para leitura e agregação). O modelo estrela é a arquitetura recomendada pela Microsoft para modelos semânticos do Power BI, porque cada visual gera consultas que filtram, agrupam e resumem; tabelas de dimensão fazem o papel de filtrar e agrupar, e tabelas de fato fazem o papel de resumir.

### 4.1 Tabelas fato

Uma tabela fato armazena eventos ou medições de negócio. Suas colunas são de dois tipos: chaves estrangeiras que apontam para dimensões e colunas numéricas mensuráveis (quantidade, valor bruto, desconto, valor líquido). Tipos clássicos de fato: fato transacional (uma linha por evento, como o item de pedido), fato de snapshot periódico (uma linha por entidade por período, como saldo de estoque no fim do dia), fato de snapshot acumulativo (uma linha por ciclo de vida, atualizada à medida que marcos ocorrem) e fato sem fatos (factless), que registra apenas a ocorrência de um evento, como presença em aula.

### 4.2 Tabelas dimensão

Uma tabela dimensão descreve as entidades pelas quais os fatos são filtrados e agrupados: quem, o quê, onde, quando. Tem uma chave única por linha e muitas colunas descritivas. As dimensões devem conter atributos textuais e hierarquias (categoria, subcategoria, produto) em uma só tabela, o que é a desnormalização controlada que distingue a estrela do floco de neve (snowflake). A tabela de datas é a dimensão mais consistente em qualquer estrela e deve ser marcada como tabela de datas no modelo, com coluna de data contígua e sem lacunas.

### 4.3 Granularidade

A granularidade (grain) define o que representa exatamente uma linha da tabela fato. Declare-a por escrito antes de qualquer outra decisão: "uma linha por item de pedido". A granularidade determina quais dimensões são válidas (um pedido tem um cliente; um item tem um produto) e impede dupla contagem. Regra prática: nunca misture granularidades distintas na mesma tabela fato; um valor de frete que existe por pedido, e não por item, precisa ser rateado ou residir em um fato de granularidade de pedido, caso contrário somas por produto o repetirão.

Dimensões degeneradas são identificadores que pertencem ao fato e não têm atributos próprios, como o número do pedido (`id_pedido`); permanecem como coluna na tabela fato.

### 4.4 Construção do fato e das dimensões em M

```m
// FatVendas — granularidade: uma linha por item de pedido
let
    Itens = Origem_ItemPedido2FN,
    Pedidos = Origem_Pedido,
    Juntado = Table.NestedJoin(
        Itens, {"id_pedido"}, Pedidos, {"id_pedido"}, "ped", JoinKind.Inner),
    Expandido = Table.ExpandTableColumn(
        Juntado, "ped", {"id_cliente", "dt_pedido", "dt_entrega"}),
    ComData = Table.TransformColumnTypes(
        Expandido, {{"dt_pedido", type date}, {"dt_entrega", type date}}),
    ComValor = Table.AddColumn(
        ComData, "valor_liquido",
        each [quantidade] * [preco_unitario], type number),
    Final = Table.SelectColumns(ComValor,
        {"id_pedido", "id_produto", "id_cliente", "dt_pedido", "dt_entrega",
         "quantidade", "preco_unitario", "valor_liquido"})
in
    Final
```

```m
// DimData — dimensão calendário contígua
let
    Inicio = #date(2020, 1, 1),
    Fim = #date(2027, 12, 31),
    Dias = List.Dates(Inicio, Duration.Days(Fim - Inicio) + 1, #duration(1, 0, 0, 0)),
    Tabela = Table.FromList(Dias, Splitter.SplitByNothing(), {"Data"}),
    Tipada = Table.TransformColumnTypes(Tabela, {{"Data", type date}}),
    ComAno = Table.AddColumn(Tipada, "Ano", each Date.Year([Data]), Int64.Type),
    ComMes = Table.AddColumn(ComAno, "MesNumero", each Date.Month([Data]), Int64.Type),
    ComNomeMes = Table.AddColumn(ComMes, "Mes",
        each Date.ToText([Data], "MMMM", "pt-BR"), type text),
    ComTrimestre = Table.AddColumn(ComNomeMes, "Trimestre",
        each "T" & Text.From(Date.QuarterOfYear([Data])), type text),
    ComAnoMes = Table.AddColumn(ComTrimestre, "AnoMes",
        each Date.Year([Data]) * 100 + Date.Month([Data]), Int64.Type)
in
    ComAnoMes
```

Observação de desempenho: calcule a coluna de ordenação (`MesNumero`) e configure "Classificar por coluna" no modelo para que os nomes de mês não apareçam em ordem alfabética.

### 4.5 Relacionamentos e cardinalidade

Um relacionamento liga uma coluna de uma tabela a uma coluna de outra e define como filtros se propagam. As cardinalidades são:

| Cardinalidade | Significado | Uso típico |
|---|---|---|
| Um para muitos (1:*) | A coluna do lado "um" é única; o lado "muitos" repete valores | Dimensão para fato; é o padrão e o recomendado |
| Muitos para um (*:1) | Equivalente ao anterior, orientação invertida | Mesmo caso |
| Um para um (1:1) | Ambas as colunas são únicas | Divisão de uma entidade em duas tabelas; frequentemente indica que as tabelas deveriam ser fundidas |
| Muitos para muitos (*:*) | Nenhum lado é único | Casos específicos; prefira tabela ponte |

O lado "um" exige valores únicos; se houver duplicatas, o Power BI rejeita a cardinalidade 1:*. Valores no fato sem correspondência na dimensão geram uma linha virtual "(Em branco)" na dimensão, sinal de problema de integridade referencial que deve ser tratado na carga (por exemplo, com um membro "Desconhecido" na dimensão).

### 4.6 Direção do filtro cruzado

A direção de filtro cruzado define para qual lado os filtros se propagam. No padrão de direção única, o filtro flui da dimensão (lado um) para o fato (lado muitos): selecionar uma categoria restringe as vendas. Na direção bidirecional, o filtro também flui do fato para a dimensão. Recomendação operacional: mantenha direção única por padrão. Bidirecional aumenta custo de consulta, pode criar caminhos ambíguos entre tabelas e interage de forma delicada com segurança em nível de linha (RLS). Quando for necessário um comportamento bidirecional apenas em uma medida, use `CROSSFILTER` ou `TREATAS` dentro de `CALCULATE`, em vez de mudar o relacionamento globalmente.

### 4.7 Relacionamentos ativos e inativos, dimensões de papel múltiplo

Só pode existir um relacionamento ativo entre duas tabelas. `FatVendas` tem duas datas (`dt_pedido`, `dt_entrega`) e ambas se relacionam com `DimData`; este é o padrão de dimensão de papel múltiplo (role-playing). Mantenha ativo o relacionamento principal e crie o outro como inativo, ativando-o por medida com `USERELATIONSHIP`.

```dax
Receita por Data de Entrega =
CALCULATE (
    [Receita],
    USERELATIONSHIP ( FatVendas[dt_entrega], DimData[Data] )
)
```

Alternativa quando se deseja usar a data de entrega em segmentações: duplicar a dimensão (`DimDataEntrega`), o que permite filtros simultâneos independentes.

### 4.8 Relacionamentos muitos-para-muitos com tabela ponte

Quando um cliente pertence a vários segmentos e um segmento contém vários clientes, crie uma tabela ponte `PonteClienteSegmento(id_cliente, id_segmento)` e dois relacionamentos 1:* partindo das dimensões `DimCliente` e `DimSegmento` para a ponte. Para que o filtro de `DimSegmento` atravesse até o fato, a propagação precisa chegar a `DimCliente`; isso exige direção bidirecional entre ponte e `DimCliente`, ou uma medida com `CROSSFILTER`/`TREATAS`.

```dax
Receita por Segmento =
CALCULATE (
    [Receita],
    CROSSFILTER ( PonteClienteSegmento[id_cliente], DimCliente[id_cliente], BOTH )
)
```

### 4.9 Dimensões de variação lenta (SCD)

SCD tipo 1 sobrescreve o atributo e perde histórico. SCD tipo 2 insere nova linha de dimensão a cada mudança, com chave substituta nova e colunas de vigência (`dt_inicio`, `dt_fim`, `flag_atual`), preservando a verdade histórica: o fato aponta para a versão da dimensão vigente na data do evento. A construção de SCD tipo 2 pertence à camada de data warehouse; no Power BI, o papel do analista é consumir a chave substituta correta.

### 4.10 Estrela versus floco de neve

No floco de neve, as dimensões permanecem normalizadas (produto → subcategoria → categoria em tabelas separadas). Isso gera mais relacionamentos, mais junções em tempo de consulta e menos clareza na lista de campos. Em Power BI, achate hierarquias na dimensão sempre que a cardinalidade permitir, mantendo o floco de neve somente quando houver razão de reuso ou volume de dimensão que o justifique.

---

## 5. Motor VertiPaq: armazenamento colunar e arquitetura de avaliação

Esta seção explica o substrato físico sobre o qual DAX é avaliado, pois diversas regras de modelagem (baixa cardinalidade, evitar colunas desnecessárias) decorrem diretamente do funcionamento do VertiPaq.

### 5.1 Armazenamento colunar e codificação

O VertiPaq armazena cada coluna separadamente, em segmentos de aproximadamente um milhão de linhas (valor padrão típico no Power BI Desktop). Cada coluna usa uma de três codificações escolhidas automaticamente: codificação por valor (para inteiros em faixa estreita, armazenados com deslocamento e menos bits), codificação por dicionário (valores distintos em um dicionário e a coluna guarda índices) e codificação hash. Sobre os índices aplica-se compressão por repetição (run-length encoding, RLE) e empacotamento de bits. A consequência prática é que o tamanho de uma coluna depende sobretudo da cardinalidade (número de valores distintos), e não apenas do número de linhas. Colunas de alta cardinalidade, como timestamps com segundos, identificadores únicos e textos livres, são as mais caras. Dividir datetime em data e hora, remover colunas não usadas e substituir texto por chaves inteiras reduz memória e acelera varreduras.

### 5.2 Storage Engine e Formula Engine

A avaliação DAX envolve dois motores. O Storage Engine (SE) executa varreduras e agregações simples sobre as colunas comprimidas, é multithread e emite consultas internas (xmSQL). O Formula Engine (FE) interpreta a expressão DAX, constrói o plano de consulta, avalia lógica que o SE não consegue expressar e é monothread. Uma medida eficiente delega ao SE o máximo possível (filtros simples em colunas, agregações) e minimiza iterações lineares e retornos do SE ao FE (callbacks). Ferramentas como DAX Studio e o Analisador de Desempenho do Power BI Desktop expõem a divisão entre tempo de SE e de FE.

---

## 6. Contexto de linha e contexto de filtro

Esta seção apresenta a diferença conceitual e matemática entre os dois contextos de avaliação de DAX. Compreendê-los é o fundamento para escrever medidas corretas e é um dos temas mais cobrados no domínio de modelagem do PL-300.

### 6.1 Contexto de filtro

O contexto de filtro é o conjunto de restrições ativas sobre colunas do modelo no momento da avaliação de uma expressão. Formalmente, pode-se vê-lo como uma função que, para cada coluna filtrada, define o subconjunto de valores permitidos; as linhas visíveis de uma tabela T são aquelas cujos valores satisfazem simultaneamente todos os filtros diretos sobre T e todos os filtros propagados por relacionamentos a partir de tabelas relacionadas. Uma agregação como `SUM(FatVendas[valor_liquido])` é, então, a soma da coluna sobre o multiconjunto de linhas visíveis de `FatVendas`. Mudar o contexto de filtro muda o conjunto de linhas somado e, portanto, o resultado.

As fontes do contexto de filtro em um relatório são: linhas e colunas de um visual (cada célula de uma matriz tem sua própria combinação de filtros), segmentações, filtros de visual, página e relatório, e filtros inseridos pela função `CALCULATE` e suas variantes. A propagação por relacionamento segue a direção do filtro cruzado: de 1 para *, por padrão.

Uma medida sempre é avaliada em um contexto de filtro, e ela se recalcula para cada célula do visual. Por isso a mesma medida `[Receita]` mostra totais distintos por categoria, por mês ou no total geral.

### 6.2 Contexto de linha

O contexto de linha é a "linha corrente" durante uma iteração. Existe em dois cenários: nas colunas calculadas (a expressão é avaliada uma vez para cada linha da tabela, e as colunas dessa linha estão acessíveis) e nas funções iteradoras (`SUMX`, `AVERAGEX`, `COUNTX`, `MAXX`, `FILTER`, `ADDCOLUMNS`, `GENERATE` e outras). Formalmente, é uma função que associa a cada coluna da tabela iterada o valor da linha atual: dentro de `SUMX(T, expr)`, para cada linha r de T, avalia-se `expr` com os valores de r e soma-se os resultados.

A diferença decisiva é a seguinte: o contexto de linha não filtra o modelo. Ele apenas fornece valores escalares da linha corrente. Por isso, em uma coluna calculada de `DimCliente`, a expressão `SUM(FatVendas[valor_liquido])` devolve o total geral das vendas para todas as linhas, pois não há filtro, apenas contexto de linha. Contexto de linha não se propaga pelos relacionamentos como filtro; para acessar colunas do lado "um" a partir do lado "muitos", usa-se `RELATED`, e para o caminho inverso `RELATEDTABLE`.

| Característica | Contexto de filtro | Contexto de linha |
|---|---|---|
| Natureza | Conjunto de restrições sobre colunas | Linha corrente de uma iteração |
| Efeito sobre agregações | Define quais linhas são agregadas | Nenhum; apenas fornece valores da linha |
| Propaga por relacionamentos | Sim, conforme direção do filtro | Não; requer `RELATED` / `RELATEDTABLE` |
| Origem | Visuais, segmentações, `CALCULATE` | Colunas calculadas, iteradores |
| Modificável por | `CALCULATE`, `ALL`, `KEEPFILTERS` etc. | Não diretamente; convertido por `CALCULATE` |

### 6.3 Exemplo comparativo

```dax
// Coluna calculada em FatVendas: contexto de linha, acessa valores da linha atual
Valor Liquido Linha = FatVendas[quantidade] * FatVendas[preco_unitario]

// Medida: contexto de filtro, agrega o conjunto de linhas visíveis
Receita = SUM ( FatVendas[valor_liquido] )

// Iterador: cria contexto de linha dentro de uma medida
Receita Iterador =
SUMX ( FatVendas, FatVendas[quantidade] * FatVendas[preco_unitario] )
```

`Receita` e `Receita Iterador` produzem o mesmo valor sob o mesmo contexto de filtro, mas o segundo calcula o produto linha a linha, útil quando não existe coluna materializada. Preferir o iterador evita uma coluna calculada e economiza memória.

### 6.4 Colunas calculadas versus medidas

Colunas calculadas são avaliadas na atualização do modelo, ocupam memória e participam de relacionamentos e segmentações. Medidas são avaliadas em consulta, não ocupam memória e reagem ao contexto de filtro. Regra: se o resultado depende da seleção do usuário (razões, médias, totais condicionais), use medida; se é um atributo estático para segmentar ou agrupar, use coluna, preferencialmente criada no Power Query ou na origem.

---

## 7. CALCULATE e transição de contexto

### 7.1 CALCULATE: sintaxe e função

`CALCULATE(<expressão>, <filtro1>, <filtro2>, ...)` avalia a expressão em um contexto de filtro modificado. É a única função DAX capaz de alterar o contexto de filtro com argumentos de filtro, e também a que converte contexto de linha em contexto de filtro. A ordem conceitual de avaliação é: os argumentos de filtro são avaliados no contexto original (incluindo o contexto de linha, se houver); se havia contexto de linha, ele é convertido em filtros (transição de contexto); os argumentos de filtro então são aplicados, sobrescrevendo filtros existentes sobre as mesmas colunas (ou combinando com eles, se `KEEPFILTERS` for usado); finalmente a expressão é avaliada.

Um argumento de filtro booleano simples como `DimProduto[nome_categoria] = "Bebidas"` é açúcar sintático para `FILTER(ALL(DimProduto[nome_categoria]), DimProduto[nome_categoria] = "Bebidas")`: ele substitui qualquer filtro existente sobre `nome_categoria` pelo novo valor.

```dax
Receita Bebidas =
CALCULATE (
    [Receita],
    DimProduto[nome_categoria] = "Bebidas"
)
```

### 7.2 Modificadores de filtro

`ALL` remove filtros de tabela ou colunas; `REMOVEFILTERS` tem efeito equivalente em CALCULATE e comunica melhor a intenção; `ALLEXCEPT` remove todos os filtros da tabela exceto os das colunas listadas; `ALLSELECTED` remove filtros de linha e coluna do visual mas preserva filtros externos (segmentações, página), sendo a base de percentuais "sobre o selecionado"; `KEEPFILTERS` faz o novo filtro intersectar o existente em vez de sobrescrevê-lo; `VALUES` e `SELECTEDVALUE` retornam os valores atualmente visíveis de uma coluna.

```dax
% do Total Geral =
DIVIDE ( [Receita], CALCULATE ( [Receita], REMOVEFILTERS ( DimProduto ) ) )

% do Total Selecionado =
DIVIDE ( [Receita], CALCULATE ( [Receita], ALLSELECTED ( DimProduto ) ) )

% da Categoria =
DIVIDE (
    [Receita],
    CALCULATE ( [Receita], ALLEXCEPT ( DimProduto, DimProduto[nome_categoria] ) )
)
```

`DIVIDE` é preferível ao operador `/` porque trata divisão por zero e valores em branco sem erro, e a Microsoft documenta seu uso como boa prática.

### 7.3 Transição de contexto

A transição de contexto ocorre quando `CALCULATE` (ou uma medida, que é implicitamente envolvida em `CALCULATE`) é avaliado dentro de um contexto de linha. Os valores de todas as colunas da linha corrente são transformados em filtros equivalentes sobre essas colunas. Em termos formais, se r é a linha corrente de T, o contexto de filtro passa a incluir `T[c1] = r[c1], T[c2] = r[c2], ...` para todas as colunas c de T. Esses filtros então se propagam por relacionamentos, afetando as tabelas do lado "muitos".

Consequência importante: a transição filtra pelas colunas da tabela, não pela identidade física da linha. Se a tabela tiver linhas duplicadas em todas as colunas, todas as duplicatas entram no filtro e o resultado as soma. Tabelas com chave única (dimensões) não sofrem esse problema; por isso a transição de contexto é segura em dimensões e perigosa em tabelas fato sem chave única.

Exemplo em coluna calculada, onde a referência a uma medida força a transição:

```dax
// Coluna calculada em DimCliente
Receita Total do Cliente = [Receita]
// Equivale a: CALCULATE ( SUM ( FatVendas[valor_liquido] ) )
// A linha corrente de DimCliente vira filtro e propaga para FatVendas.
```

Exemplo em iterador, onde a transição ocorre a cada iteração:

```dax
Clientes Acima da Media =
VAR MediaReceita =
    AVERAGEX ( ALL ( DimCliente[id_cliente] ), [Receita] )
RETURN
    COUNTROWS (
        FILTER ( VALUES ( DimCliente[id_cliente] ), [Receita] > MediaReceita )
    )
```

Aqui, `AVERAGEX` itera sobre cada cliente (contexto de linha), e a referência a `[Receita]` provoca transição: para cada cliente, a receita é calculada apenas com suas vendas. `ALL` remove os filtros prévios de cliente para calcular a média sobre o universo completo. O mesmo raciocínio vale em `FILTER`, onde `[Receita]` é reavaliada para cada cliente visível.

Alerta de desempenho: a transição de contexto em iterações sobre tabelas grandes é custosa, pois cada linha dispara uma avaliação de CALCULATE. Itere sobre colunas de baixa cardinalidade (`VALUES(DimCliente[id_cliente])`) e não sobre a tabela fato inteira quando a medida depender de transição.

### 7.4 Variáveis

`VAR`/`RETURN` avalia a expressão uma única vez, no contexto em que a variável é declarada, e reutiliza o resultado. Variáveis melhoram legibilidade e desempenho, e fixam o valor no contexto original, impedindo que alterações de contexto posteriores (por `CALCULATE`) mudem o resultado.

```dax
Crescimento Receita % =
VAR Atual = [Receita]
VAR Anterior = CALCULATE ( [Receita], SAMEPERIODLASTYEAR ( DimData[Data] ) )
RETURN
    DIVIDE ( Atual - Anterior, Anterior )
```

---

## 8. Inteligência de tempo em DAX

Funções de inteligência de tempo exigem uma tabela de datas contígua, relacionada ao fato por uma coluna de data, e preferencialmente marcada como tabela de datas. Sem calendário contíguo, funções como `SAMEPERIODLASTYEAR` e `DATESYTD` produzem resultados incorretos ou vazios. A documentação de orientação do Power BI sobre tabelas de datas está listada na seção 9.

### 8.1 Acumulados no período

```dax
Receita YTD = TOTALYTD ( [Receita], DimData[Data] )

Receita MTD = TOTALMTD ( [Receita], DimData[Data] )

Receita QTD = TOTALQTD ( [Receita], DimData[Data] )

// Forma explícita equivalente a TOTALYTD, mais flexível
Receita YTD CALCULATE =
CALCULATE ( [Receita], DATESYTD ( DimData[Data] ) )

// Ano fiscal terminando em 30 de junho
Receita YTD Fiscal =
CALCULATE ( [Receita], DATESYTD ( DimData[Data], "6-30" ) )
```

### 8.2 Comparações com períodos anteriores

```dax
Receita Ano Anterior =
CALCULATE ( [Receita], SAMEPERIODLASTYEAR ( DimData[Data] ) )

Receita Mes Anterior =
CALCULATE ( [Receita], DATEADD ( DimData[Data], -1, MONTH ) )

Receita Trimestre Anterior =
CALCULATE ( [Receita], PARALLELPERIOD ( DimData[Data], -1, QUARTER ) )

Variacao YoY % =
VAR Atual = [Receita]
VAR Anterior = [Receita Ano Anterior]
RETURN
    DIVIDE ( Atual - Anterior, Anterior )
```

`DATEADD` desloca o conjunto de datas atual por um intervalo; `PARALLELPERIOD` retorna períodos completos (por exemplo, o trimestre inteiro anterior, mesmo que o contexto atual cubra apenas parte dele); `SAMEPERIODLASTYEAR` é atalho para `DATEADD(..., -1, YEAR)`.

### 8.3 Janelas móveis

```dax
Receita Ultimos 12 Meses =
CALCULATE (
    [Receita],
    DATESINPERIOD ( DimData[Data], MAX ( DimData[Data] ), -12, MONTH )
)

Media Movel 3 Meses =
VAR UltimaData = MAX ( DimData[Data] )
VAR Janela = DATESINPERIOD ( DimData[Data], UltimaData, -3, MONTH )
RETURN
    AVERAGEX (
        VALUES ( DimData[AnoMes] ),
        CALCULATE ( [Receita], Janela )
    )
```

No exemplo da média móvel, a variável `Janela` captura a tabela de datas no contexto original; a média é calculada sobre os valores de `Receita` por mês dentro da janela de três meses. Em visuais em nível de mês, a granularidade da iteração deve ser coerente com a janela.

### 8.4 Medidas semiaditivas (saldos e estoque)

Um saldo de estoque é aditivo entre produtos, mas não entre datas: somar o estoque de todos os dias de um mês não faz sentido. A medida correta usa o último valor do período.

```dax
Estoque Final =
CALCULATE (
    SUM ( FatEstoque[quantidade] ),
    LASTNONBLANK ( DimData[Data], CALCULATE ( COUNTROWS ( FatEstoque ) ) )
)
```

`LASTNONBLANK` pega a última data do contexto em que existe registro de estoque, o que evita saldo em branco quando o último dia do mês não tem linha.

### 8.5 Acumulado até a data corrente do contexto (running total)

```dax
Receita Acumulada =
CALCULATE (
    [Receita],
    FILTER ( ALL ( DimData[Data] ), DimData[Data] <= MAX ( DimData[Data] ) )
)
```

---

## 9. Documentação oficial e fontes complementares para ingestão

As fontes abaixo foram selecionadas para agregar à base de conhecimento. Os primeiros itens foram abertos e confirmados durante a pesquisa que gerou este manual; os demais são páginas oficiais estáveis da Microsoft e de referências consolidadas da comunidade, e devem ter o link validado no momento do download, já que a Microsoft reorganiza caminhos de vez em quando.

### 9.1 Confirmadas durante a pesquisa

| Tema | Link |
|---|---|
| Conector PostgreSQL no Power Query (query folding nativo, EnableFolding) | https://learn.microsoft.com/power-query/connectors/postgresql |
| Entenda o esquema estrela e sua importância para o Power BI | https://learn.microsoft.com/power-bi/guidance/star-schema |
| Índice de diretrizes (guidance) do Power BI | https://learn.microsoft.com/power-bi/guidance/overview |
| Módulo Learn: modificar o contexto de filtro com CALCULATE e transição de contexto | https://learn.microsoft.com/en-us/training/modules/dax-power-bi-modify-filter/ |
| Módulo Learn: construir o modelo de dados para o Power BI | https://learn.microsoft.com/en-us/training/modules/build-power-bi-report/2-build-data-model |
| Referência comunitária de Value.NativeQuery (folding, PreserveTypes) | https://powerquery.how/value-nativequery/ |
| Repositório do livro de estudo oficial do PL-300 (Packt) | https://github.com/PacktPublishing/Microsoft-Power-BI-Data-Analyst-Study-Guide |
| Guia de estudo PL-300 mantido no GitHub (conteúdo de 2022, usar com cautela) | https://github.com/AzAdminEVM/Power-BI-PL-300-Study-Guide |

### 9.2 Páginas oficiais e de referência para baixar e validar

| Tema | Link |
|---|---|
| Página do exame PL-300 e outline de habilidades | https://learn.microsoft.com/credentials/certifications/exams/pl-300/ |
| Documentação do Power Query | https://learn.microsoft.com/power-query/ |
| Fundamentos de query folding | https://learn.microsoft.com/power-query/query-folding-basics |
| Importar dados de banco com consulta nativa | https://learn.microsoft.com/power-query/native-database-query |
| Referência da linguagem M | https://learn.microsoft.com/powerquery-m/ |
| Referência de funções DAX | https://learn.microsoft.com/dax/ |
| Função CALCULATE (DAX) | https://learn.microsoft.com/dax/calculate-function-dax |
| Funções de inteligência de tempo (DAX) | https://learn.microsoft.com/dax/time-intelligence-functions-dax |
| Relacionamentos de modelo no Power BI Desktop | https://learn.microsoft.com/power-bi/transform-model/desktop-relationships-understand |
| Diretriz: tabelas de datas | https://learn.microsoft.com/power-bi/guidance/model-date-tables |
| Diretriz: relacionamentos ativos e inativos | https://learn.microsoft.com/power-bi/guidance/relationships-active-inactive |
| Diretriz: filtragem bidirecional | https://learn.microsoft.com/power-bi/guidance/relationships-bidirectional-filtering |
| Diretriz: relacionamentos muitos-para-muitos | https://learn.microsoft.com/power-bi/guidance/relationships-many-to-many |
| Dicionário de funções DAX com exemplos (SQLBI) | https://dax.guide/ |
| Artigos e guias de DAX avançado, contexto e VertiPaq (SQLBI) | https://www.sqlbi.com/ |
| Técnicas de modelagem dimensional (Kimball Group) | https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/ |

Sugestão de ingestão: baixe cada página como HTML ou Markdown limpo, preserve o título e a URL como metadados do fragmento, e mantenha este manual como documento-âncora; os fragmentos oficiais atuam como evidência de apoio e permitem rastrear cada afirmação técnica até a fonte.

---

## 10. Mapa de conteúdo para o exame PL-300

Esta seção relaciona o conteúdo do manual às competências medidas, para orientar a priorização de estudo. O exame é organizado em quatro grandes áreas: preparar os dados, modelar os dados, visualizar e analisar os dados, e gerenciar e proteger o Power BI. Este manual cobre as duas primeiras de forma aprofundada e a parte de cálculo da terceira.

| Competência cobrada | Seções do manual |
|---|---|
| Obter dados de fontes e configurar conexões | 2 |
| Perfilar, limpar e transformar dados | 3 |
| Query folding, consultas de referência e parâmetros | 2.3, 3.6 |
| Projetar um modelo de dados com esquema estrela | 4 |
| Relacionamentos, cardinalidade e direção de filtro | 4.5 a 4.8 |
| Criar tabelas e colunas calculadas | 4.4, 6.4 |
| Criar medidas, usar CALCULATE e funções de tabela | 7 |
| Contexto de linha e de filtro | 6 |
| Inteligência de tempo | 8 |
| Otimizar desempenho do modelo | 5, 6.4, 7.3 |

### 10.1 Armadilhas recorrentes

Usar coluna calculada onde medida é necessária e obter total incorreto em visuais com contexto variável. Esquecer que `SUM` em coluna calculada sem `CALCULATE` ignora a linha corrente por não haver transição. Criar relacionamento bidirecional por conveniência e introduzir ambiguidade. Calcular inteligência de tempo sem tabela de datas contígua ou sem relacionar a coluna de data do fato a ela. Aplicar `Table.Distinct` sem validar a dependência funcional e perder dados silenciosamente. Dobrar mal a consulta e puxar a tabela inteira para o Power Query antes de filtrar. Misturar granularidades no mesmo fato e duplicar valores em somas por dimensão.

### 10.2 Glossário técnico de referência rápida

Fato: tabela de eventos mensuráveis. Dimensão: tabela de atributos descritivos usada para filtrar e agrupar. Granularidade: significado exato de uma linha do fato. Chave substituta: identificador artificial único de uma linha de dimensão. Dimensão degenerada: identificador mantido no fato sem tabela própria. Dimensão de papel múltiplo: mesma dimensão usada em mais de um papel (data do pedido, data de entrega). Query folding: tradução de passos de M em SQL executado no servidor. Contexto de filtro: conjunto de restrições ativas sobre colunas. Contexto de linha: linha corrente de uma iteração. Transição de contexto: conversão do contexto de linha em contexto de filtro por CALCULATE. Medida semiaditiva: medida que soma por algumas dimensões mas não por outras, tipicamente o tempo. Storage Engine: motor de varredura e agregação sobre dados comprimidos. Formula Engine: motor que interpreta DAX e constrói o plano de consulta.
