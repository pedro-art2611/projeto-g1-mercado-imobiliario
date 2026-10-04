from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from sqlalchemy import create_engine, text

RAIZ = Path(__file__).resolve().parent
BANCO = RAIZ / 'database' / 'mercado_imobiliario.sqlite'
CSV = RAIZ / 'dados' / 'simulacao_mercado_imobiliario_brasil.csv'
NUMERICAS = ['area_m2', 'quartos', 'vagas_garagem', 'preco_imovel',
             'preco_m2', 'renda_media', 'taxa_juros']
ROTULOS = {'area_m2': 'Área (m²)', 'quartos': 'Quartos', 'vagas_garagem': 'Vagas',
           'preco_imovel': 'Preço do imóvel (R$)', 'preco_m2': 'Preço por m² (R$)',
           'renda_media': 'Renda média (R$)', 'taxa_juros': 'Juros (%)',
           'tipo_imovel': 'Tipo de imóvel', 'cidade': 'Cidade', 'regiao': 'Região',
           'uf': 'UF', 'data': 'Mês', 'nivel_preco': 'Nível de preço'}


def br(valor, casas=2):
    return f'{valor:,.{casas}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def narrar(texto):
    st.markdown(texto.replace('$', r'\$'))


@st.cache_data
def carregar_dados():
    BANCO.parent.mkdir(exist_ok=True)
    engine = create_engine(f'sqlite:///{BANCO.as_posix()}')
    try:
        if not BANCO.exists():
            base = pd.read_csv(CSV, parse_dates=['data'])
            base['ano_mes'] = base.data.dt.strftime('%Y-%m')
            with engine.begin() as conexao:
                base.to_sql('mercado_imobiliario', conexao, index=False, if_exists='fail')
        with engine.connect() as conexao:
            dados = pd.read_sql(text('SELECT * FROM mercado_imobiliario'), conexao)
        dados['data'] = pd.to_datetime(dados['data'])
        return dados.sort_values('data')
    finally:
        engine.dispose()


def serie_mensal(dados):
    serie = dados.groupby('data').preco_m2.median().sort_index().to_frame('mediana')
    if not serie.empty:
        # Reindexar evita chamar 12 observações espaçadas de 12 meses consecutivos.
        serie = serie.reindex(pd.date_range(serie.index.min(), serie.index.max(), freq='MS'))
    serie['media_movel'] = serie.mediana.rolling(12, min_periods=12).mean()
    return serie


def correlacoes(dados):
    matriz = dados[NUMERICAS].corr()
    pares = matriz.where(np.triu(np.ones(matriz.shape), k=1).astype(bool)).stack().dropna()
    if pares.empty:
        return matriz, None, None
    par = pares.abs().idxmax()
    return matriz, par, float(pares.loc[par])


def selecionar(titulo, coluna, dados):
    opcoes = sorted(dados[coluna].dropna().unique())
    chave = f'filtro_{coluna}'
    if chave in st.session_state:
        st.session_state[chave] = [x for x in st.session_state[chave] if x in opcoes]
    return st.sidebar.multiselect(titulo, opcoes, key=chave,
                                  placeholder='Todas as opções',
                                  help='Sem seleção, inclui todas as opções disponíveis.')


def aplicar(dados, coluna, selecao):
    return dados[dados[coluna].isin(selecao)] if selecao else dados


def mostrar_plotly(fig):
    fig.update_layout(template='plotly_white', margin=dict(l=10, r=10, t=55, b=10),
                      separators=',.', font=dict(size=13), legend_title_text='')
    st.plotly_chart(fig, width='stretch')


def main():
    st.set_page_config(page_title='Mercado Imobiliário Brasileiro | G1', layout='wide')
    st.markdown('<style>[data-testid="stMetricValue"]{font-size:clamp(1rem,1.6vw,1.6rem)} [data-testid="stMetricLabel"] p{white-space:normal}</style>', unsafe_allow_html=True)
    st.title('Mercado Imobiliário Brasileiro')
    st.write('Análise de preços e comportamento na base simulada entre 2015 e 2024.')
    st.caption('Pedro Artur Brandão Murillo | Professor Alexandre Neves Louzada | Avaliação G1')
    st.caption('Linguagem de Programação: Análise e Visualização de Dados com Python')
    st.info('Dados simulados para atividade acadêmica. O preço por m² é o campo original da base, que diverge da razão entre preço e área. Os resultados não representam o mercado real brasileiro.')
    dados = carregar_dados()
    st.sidebar.header('Recorte da análise')
    meses = sorted(dados.ano_mes.unique())
    inicio, fim = st.sidebar.select_slider('Período', options=meses, value=(meses[0], meses[-1]))
    recorte = dados[dados.ano_mes.between(inicio, fim)]
    recorte = aplicar(recorte, 'regiao', selecionar('Região', 'regiao', recorte))
    recorte = aplicar(recorte, 'uf', selecionar('UF', 'uf', recorte))
    recorte = aplicar(recorte, 'cidade', selecionar('Cidade', 'cidade', recorte))
    recorte = aplicar(recorte, 'tipo_imovel', selecionar('Tipo de imóvel', 'tipo_imovel', recorte))
    recorte = aplicar(recorte, 'nivel_preco', selecionar('Nível de preço', 'nivel_preco', recorte))
    st.sidebar.caption('As opções geográficas acompanham as seleções anteriores. Seleção vazia inclui todas as opções. A cobertura contém 20 UFs, não o país inteiro.')
    if recorte.empty:
        st.warning('Nenhum registro corresponde ao recorte. Amplie o período ou remova uma seleção.')
        return

    mensal = serie_mensal(recorte)
    observados = mensal.mediana.dropna()
    variacao = (observados.iloc[-1] / observados.iloc[0] - 1) * 100 if len(observados) > 1 else None
    matriz, par, coef = correlacoes(recorte)
    cols = st.columns(5)
    cols[0].metric('Preço mediano do imóvel', f'R$ {br(recorte.preco_imovel.median())}')
    cols[1].metric('Preço mediano por m²', f'R$ {br(recorte.preco_m2.median())}',
                   delta=f'{br(variacao)}% entre meses extremos' if variacao is not None else None,
                   delta_color='off')
    cols[2].metric('Área mediana', f'{br(recorte.area_m2.median(), 0)} m²')
    cols[3].metric('Taxa média de juros', f'{br(recorte.taxa_juros.mean())}%')
    cols[4].metric('Registros analisados', br(len(recorte), 0))
    abas = st.tabs(['Visão geral', 'Evolução temporal', 'Análise geográfica',
                    'Perfil dos imóveis', 'Relações estatísticas', 'Dados'])
    with abas[0]:
        st.subheader('Distribuição dos preços')
        mostrar_plotly(px.histogram(recorte, x='preco_imovel', nbins=40,
                                    labels=ROTULOS, title='Preço do imóvel no recorte',
                                    color_discrete_sequence=['#187a89']).update_layout(yaxis_title='Registros'))
        st.write(f'O recorte reúne {br(len(recorte),0)} registros de {recorte.cidade.nunique()} cidades e {recorte.uf.nunique()} UFs, em {len(observados)} meses. A mediana do preço do imóvel é R$ {br(recorte.preco_imovel.median())}.')
        q1, q3 = recorte.preco_imovel.quantile([.25, .75])
        extremos = ((recorte.preco_imovel < q1 - 1.5*(q3-q1)) | (recorte.preco_imovel > q3 + 1.5*(q3-q1))).sum()
        st.caption(f'O IQR calculado neste recorte identifica {extremos} valores extremos. Eles permanecem na análise; a classificação não comprova erro.')
    with abas[1]:
        st.subheader('Mediana mensal do preço por m²')
        fig = go.Figure()
        for campo, nome, cor in [('mediana', 'Mediana mensal', '#187a89'), ('media_movel', 'Média móvel de 12 meses', '#d78b37')]:
            fig.add_trace(go.Scatter(x=mensal.index, y=mensal[campo], name=nome,
                                     line=dict(color=cor), connectgaps=False,
                                     hovertemplate='%{x|%m/%Y}<br>R$ %{y:,.2f}/m²<extra>%{fullData.name}</extra>'))
        fig.update_layout(title='Preço por m² fornecido e média móvel', xaxis_title='Mês', yaxis_title='Preço (R$/m²)', yaxis_tickprefix='R$ ')
        mostrar_plotly(fig)
        if variacao is None:
            st.write('O recorte contém um único mês. Não é possível comparar períodos distintos.')
        else:
            narrar(f'Entre {observados.index[0]:%m/%Y} e {observados.index[-1]:%m/%Y}, a mediana mensal passou de R$ {br(observados.iloc[0])} para R$ {br(observados.iloc[-1])}, variação de {br(variacao)}%. A diferença entre extremos não demonstra uma trajetória contínua.')
        st.caption('A média móvel exige 12 meses consecutivos com dados. Os valores são nominais, sem ajuste de inflação.')
    with abas[2]:
        nivel = st.radio('Comparar por', ['Região', 'UF', 'Cidade'], horizontal=True)
        coluna = {'Região':'regiao', 'UF':'uf', 'Cidade':'cidade'}[nivel]
        geo = recorte.groupby(coluna).agg(mediana=('preco_m2','median'), registros=('preco_m2','size')).sort_values('mediana').reset_index()
        fig = px.bar(geo, x='mediana', y=coluna, orientation='h', hover_data=['registros'],
                     title=f'Mediana do preço por m² por {nivel.lower()}',
                     labels={**ROTULOS, 'mediana':'Mediana (R$/m²)', 'registros':'Registros'},
                     color_discrete_sequence=['#187a89'], height=max(380, len(geo)*24))
        fig.update_layout(yaxis=dict(categoryorder='array', categoryarray=geo[coluna].tolist()), xaxis_tickprefix='R$ ')
        mostrar_plotly(fig)
        lider = geo.iloc[-1]
        st.write(f'{lider[coluna]} tem a maior mediana neste agrupamento: R$ {br(lider.mediana)}/m², com {br(lider.registros,0)} registros. A comparação se limita às localidades presentes no recorte.')
    with abas[3]:
        st.subheader('Preço por tipo de imóvel')
        fig, ax = plt.subplots(figsize=(11,5))
        sns.boxplot(data=recorte, x='tipo_imovel', y='preco_imovel', color='#9bc9cf', ax=ax)
        ax.set(xlabel='Tipo de imóvel', ylabel='Preço do imóvel (R$)')
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        perfil = recorte.groupby('tipo_imovel')[['preco_imovel','area_m2','quartos','vagas_garagem']].median()
        st.dataframe(perfil.rename(columns=ROTULOS), width='stretch')
        mostrar_plotly(px.scatter(recorte, x='area_m2', y='preco_imovel', color='tipo_imovel',
                                   hover_data=['cidade','quartos','vagas_garagem'], labels=ROTULOS,
                                   title='Área e preço do imóvel'))
        tipo = perfil.preco_imovel.idxmax()
        st.write(f'{tipo} apresenta o maior preço mediano por tipo no recorte: R$ {br(perfil.loc[tipo,"preco_imovel"])}. A área mediana do recorte é {br(recorte.area_m2.median(),0)} m², com medianas de {br(recorte.quartos.median(),1)} quartos e {br(recorte.vagas_garagem.median(),1)} vagas.')
    with abas[4]:
        st.subheader('Associações lineares')
        if len(recorte) < 30:
            st.warning('O recorte possui menos de 30 registros. Interprete as correlações com cautela.')
        if coef is None:
            st.write('Não há variabilidade ou registros suficientes para calcular associações entre pares.')
        else:
            fig, ax = plt.subplots(figsize=(10,7))
            sns.heatmap(matriz.rename(index=ROTULOS,columns=ROTULOS), annot=True, fmt='.2f',
                        cmap='RdBu_r', vmin=-1, vmax=1, center=0, ax=ax)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            forca = 'fraca' if abs(coef)<.3 else 'moderada' if abs(coef)<.7 else 'forte'
            st.write(f'A maior associação linear em magnitude é {forca}, entre {ROTULOS[par[0]]} e {ROTULOS[par[1]]}: r = {br(coef,3)}. Correlação não estabelece causalidade.')
        st.caption('Pearson usa as sete variáveis numéricas. Valores constantes não produzem correlação definida.')
    with abas[5]:
        st.write(f'{br(len(recorte),0)} registros no recorte atual.')
        st.dataframe(recorte, width='stretch', hide_index=True)
        st.download_button('Baixar recorte em CSV', recorte.to_csv(index=False).encode('utf-8-sig'),
                           file_name='recorte_mercado_imobiliario.csv', mime='text/csv')
        st.caption('O download contém os dados filtrados e ano_mes. O CSV original permanece preservado no repositório.')
    st.divider()
    st.subheader('Conclusão do recorte')
    cidades = recorte.groupby('cidade').preco_m2.median()
    temporal = f'A variação entre os meses extremos foi {br(variacao)}%.' if variacao is not None else 'Há apenas um mês disponível para análise temporal.'
    associacao = f'A maior correlação absoluta foi {br(abs(coef),3)}.' if coef is not None else 'As correlações não puderam ser estimadas.'
    narrar(f'O preço mediano é R$ {br(recorte.preco_imovel.median())}, e a mediana por m² é R$ {br(recorte.preco_m2.median())}. {cidades.idxmax()} apresenta a maior mediana por m² entre as cidades selecionadas. {temporal} {associacao} Estas conclusões descrevem a base simulada filtrada.')


if __name__ == '__main__':
    main()
