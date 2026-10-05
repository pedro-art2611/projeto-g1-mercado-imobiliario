# Mercado Imobiliário Brasileiro

Análise dos preços e do perfil dos imóveis em uma base simulada de 2015 a 2024. O projeto reúne a exploração dos dados em Python e um dashboard para comparar períodos, localidades e características dos imóveis.

[Dashboard Streamlit](https://projeto-g1-mercado-imobiliario-9njgs7po5ls3yj7mvsc9kx.streamlit.app/) | [Apresentação no GitHub Pages](https://pedro-art2611.github.io/projeto-g1-mercado-imobiliario/)

## Identificação acadêmica

- Aluno: Pedro Artur Brandão Murillo
- Professor: Alexandre Neves Louzada
- Disciplina: Linguagens de Programação
- Avaliação: G1
- Tema 12: Mercado Imobiliário Brasileiro

## Sobre o projeto

O mercado imobiliário foi o tema escolhido para estudar a distribuição dos preços e suas diferenças conforme a localização e o perfil dos imóveis. A base reúne preços, área, quartos, vagas de garagem, renda média e taxa de juros, permitindo comparar esses aspectos ao longo de dez anos.

A pergunta central é: **como os preços dos imóveis se comportam na base simulada do mercado imobiliário brasileiro entre 2015 e 2024, considerando localização, características dos imóveis e indicadores econômicos?**

O trabalho foi desenvolvido na avaliação G1 para aplicar a análise e a visualização de dados com Python. O notebook apresenta os cálculos e a interpretação dos resultados; o dashboard permite explorar a mesma base com filtros e gráficos interativos.

## Base de dados

O projeto utiliza a base [simulacao_mercado_imobiliario_brasil.csv](https://github.com/AlexandreLouzada/Dados-Simulados-G2/blob/main/datasets_g2_30_temas/simulacao_mercado_imobiliario_brasil.csv), disponibilizada para o Tema 12 da atividade.

São 4.440 registros e 16 colunas, distribuídos em 120 meses, de janeiro de 2015 a dezembro de 2024. Cada mês possui uma observação por cidade. A cobertura inclui 37 cidades, 20 UFs e as cinco regiões brasileiras.

As colunas descrevem o período, a localização, o tipo de imóvel, a área, os quartos, as vagas, os preços e os indicadores econômicos. A base é simulada e não representa todo o mercado imobiliário brasileiro.

## O que foi analisado

- A distribuição dos preços dos imóveis, do preço por m² e da área.
- A evolução mensal do preço por m² e sua média móvel de 12 meses.
- As diferenças entre regiões, UFs e cidades presentes na base.
- O perfil dos imóveis por tipo, área, número de quartos e vagas.
- As correlações entre preços, características dos imóveis, renda média e juros.
- A consistência do preço por m² informado em relação ao preço e à área.

## Principais resultados

| Indicador da base completa | Resultado |
| --- | ---: |
| Preço mediano do imóvel | R$ 537.645,22 |
| Preço mediano por m² | R$ 10.968,15 |
| Área mediana | 121 m² |
| Taxa média de juros | 10,52% |
| Registros analisados | 4.440 |

A mediana mensal do preço por m² foi de R$ 11.564,40 em janeiro de 2015 e R$ 12.048,09 em dezembro de 2024, uma variação de 4,18%. Entre esses dois meses, a série apresenta oscilações. A diferença entre o primeiro e o último valor não significa que os preços tenham subido continuamente.

Centro-Oeste apresenta a maior mediana regional por m². Entre as cidades da base, Petrópolis tem a maior mediana. Essas comparações se referem apenas aos registros simulados e às localidades presentes.

As correlações lineares entre as sete variáveis numéricas são fracas. A maior magnitude é próxima de 0,034, entre vagas de garagem e renda média (r = -0,0337). Esses valores não sustentam uma relação linear forte nem uma explicação causal para os preços.

## Tratamento dos dados

Antes da análise, foram verificados valores ausentes, duplicatas, datas, valores inválidos e a consistência das relações entre cidade, UF e região. Não foram encontrados problemas que exigissem a remoção de linhas. A coluna `data` foi convertida para `datetime`, e `ano_mes` foi criada para organizar os períodos.

O intervalo interquartil (IQR) identificou 248 preços extremos, equivalentes a 5,59% dos registros. Esses valores foram mantidos: preços elevados podem ocorrer em dados imobiliários, e a classificação pelo IQR, por si só, não indica um erro. Por isso, a mediana foi utilizada nas principais comparações de preço.

Também foi calculada a razão `preco_m2_calculado = preco_imovel / area_m2` para comparar com o preço por m² informado. A correlação entre os dois é -0,0175, e a diferença relativa absoluta mediana é 63,64%. Nesta simulação, os campos não são matematicamente equivalentes. O cálculo ficou restrito à verificação no notebook; o dashboard utiliza `preco_m2` original, e o CSV não foi alterado.

## Dashboard

O [dashboard do projeto](https://projeto-g1-mercado-imobiliario-9njgs7po5ls3yj7mvsc9kx.streamlit.app/) permite filtrar período, região, UF, cidade, tipo de imóvel e nível de preço. As opções de UF e cidade acompanham a seleção geográfica, e os KPIs, gráficos e textos mudam conforme o recorte.

As abas apresentam a distribuição dos preços, a evolução mensal com média móvel de 12 meses e as comparações geográficas. O perfil dos imóveis pode ser explorado pelo boxplot de preços por tipo e pelo gráfico de dispersão entre área e preço. A matriz de correlação reúne as associações entre as variáveis numéricas.

Na aba de dados, é possível consultar a tabela filtrada e baixar o recorte em CSV. Ao final da página, uma conclusão resume os resultados da seleção atual.

![Dashboard do projeto](imagens/dashboard-preview.png)

## Tecnologias

| Tecnologia | Onde foi utilizada |
| --- | --- |
| Python | Código da análise e do dashboard |
| Pandas | Leitura, preparação, agrupamentos, KPIs, média móvel e correlação |
| NumPy | Comparação numérica do preço por m² e seleção dos pares de correlação |
| Matplotlib | Figuras estáticas, eixos e formatação dos gráficos |
| Seaborn | Histogramas, boxplot e matriz de correlação |
| Plotly | Gráficos interativos de distribuição, tempo, localização e dispersão |
| Streamlit | Interface do dashboard, filtros, abas e tabela de dados |
| SQLAlchemy | Conexão, gravação e consultas ao banco |
| SQLite | Armazenamento dos registros preparados |
| GitHub | Versionamento do código, acesso ao notebook e publicação da apresentação |

## Funcionalidades implementadas

O dashboard combina filtros múltiplos, KPIs dinâmicos e gráficos interativos em seis abas. A análise temporal inclui a mediana mensal e a média móvel de 12 meses; as comparações geográficas permitem alternar entre região, UF e cidade.

A persistência usa **SQLite com SQLAlchemy**, na tabela `mercado_imobiliario`. O notebook grava a base preparada e apresenta uma consulta SQL. O app lê esse banco com cache e, caso o arquivo não exista, cria a tabela a partir do CSV.

A **correlação estatística** compara área, quartos, vagas, preço do imóvel, preço por m², renda média e taxa de juros. A matriz é acompanhada de uma interpretação, com um aviso de cautela quando o recorte possui poucos registros.

## Estrutura do projeto

```text
projeto-g1-mercado-imobiliario/
├── app.py
├── requirements.txt
├── README.md
├── index.html
├── dados/
│   └── simulacao_mercado_imobiliario_brasil.csv
├── database/
│   └── mercado_imobiliario.sqlite
├── notebooks/
│   └── analise_mercado_imobiliario.ipynb
└── imagens/
    └── dashboard-preview.png
```

## Como executar

Utilize Python 3.12 ou superior. Para baixar o projeto e criar o ambiente virtual:

```bash
git clone https://github.com/pedro-art2611/projeto-g1-mercado-imobiliario.git
cd projeto-g1-mercado-imobiliario
python -m venv .venv
```

Ative o ambiente no Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale as dependências e inicie o dashboard:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

### Reexecutar o notebook

Na raiz do projeto, com o ambiente virtual ativo:

```bash
python -m pip install jupyter nbconvert ipykernel
jupyter nbconvert --to notebook --execute --inplace notebooks/analise_mercado_imobiliario.ipynb
```

Esse comando atualiza as saídas do notebook e recria a tabela SQLite, sem alterar o CSV. As ferramentas Jupyter são necessárias apenas para trabalhar com o notebook.

## Links

- [Repositório](https://github.com/pedro-art2611/projeto-g1-mercado-imobiliario)
- [GitHub Pages](https://pedro-art2611.github.io/projeto-g1-mercado-imobiliario/)
- [Dashboard Streamlit](https://projeto-g1-mercado-imobiliario-9njgs7po5ls3yj7mvsc9kx.streamlit.app/)
- [Notebook](https://github.com/pedro-art2611/projeto-g1-mercado-imobiliario/blob/main/notebooks/analise_mercado_imobiliario.ipynb)

## Limitações

A base é simulada e cobre 20 UFs, não todas as UFs brasileiras. Os preços são nominais, sem ajuste de inflação, e os registros não acompanham imóveis individuais ao longo do tempo.

O campo `preco_m2` fornecido não corresponde matematicamente à razão entre preço e área. Da mesma forma, `nivel_preco` é usado como categoria exploratória, sem interpretá-lo como uma escala quantitativa.

## Conclusão

A base apresenta grande dispersão de preços e oscilações mensais. A mediana ajuda a comparar os registros sem deixar que os valores extremos dominem o resumo, enquanto a média móvel facilita a leitura do comportamento ao longo do período.

As diferenças entre localidades e perfis descrevem o conjunto analisado, mas as correlações lineares são fracas. Os resultados permitem discutir o comportamento desta simulação, sem extrapolá-lo para o mercado imobiliário brasileiro real.
