import pandas as pd 
import streamlit as st 
import plotly.express as px


st.set_page_config(
    page_title='Salario da area de Dados - Gabriel',
    page_icon='💡',
    layout='wide',
)

df = pd.read_csv("https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv")

df = df.rename(columns={
    'work_year': 'ano_trabalho',
    'experience_level': 'nivel_experiencia',
    'employment_type': 'tipo_contratacao',
    'job_title': 'cargo',
    'salary': 'salario',
    'salary_currency': 'moeda_salario',
    'salary_in_usd': 'salario_em_usd',
    'employee_residence': 'residencia_funcionario',
    'remote_ratio': 'percentual_remoto',
    'company_location': 'localizacao_empresa',
    'company_size': 'porte_empresa'
})

novo_nivel = {
    'EN': 'Junior',
    'MI': 'Pleno',
    'SE': 'Senior',
    'EX': 'Executivo',
}
df['nivel_experiencia'] = df['nivel_experiencia'].map(novo_nivel)

df['percentual_remoto'] = df['percentual_remoto'].replace({
    0: 'Presencial',
    50: 'Híbrido', 
    100: 'Remoto',
    })


tipo_contratato = {
    'FT': 'Integral',
    'PT': 'Parcial',
    'CT': 'CLT',
    'FL': 'Freelance',
}
df['tipo_contratacao'] = df['tipo_contratacao'].replace(tipo_contratato)
df['tipo_contratacao'].value_counts()

cargos_pt = {
    'Data Scientist': 'Cientista de Dados',
    'Data Engineer': 'Engenheiro de Dados',
    'Data Analyst': 'Analista de Dados',
    'Machine Learning Engineer': 'Engenheiro de Machine Learning',
    'Engineer': 'Engenheiro',
    'Quantitative Research Analyst ': 'Analista de Pesquisa Quantitativa',
    'CRM Data Analyst': 'Analista de Dados CRM',
    'Lead AI Engineer': 'Lider de IA',
    'Cloud Data Architect':'Arquiteto de Dados em Nuvem',
    'Principal Data Architect': 'Arquiteto de Dados Principal',
}
df['cargo'] = df['cargo'].replace(cargos_pt)
df['cargo'].value_counts()

df.isnull().sum()
media_ano = df['ano_trabalho'].median()
df['ano_trabalho'] = df['ano_trabalho'].fillna(media_ano)
df['ano_trabalho'] = df['ano_trabalho'].astype(int)


st.sidebar.header('🕵️‍♂️Filtros')

anos_disponiveis = sorted(df['ano_trabalho'].unique())
anos_selecionados = st.sidebar.multiselect('Selecione o(s) ano(s):', anos_disponiveis, default=anos_disponiveis)

senioridade_disponiveis = sorted(df['nivel_experiencia'].unique())
senioridade_selecionada = st.sidebar.multiselect('Selecione o(s) nível(is) de senioridade:', senioridade_disponiveis, default=senioridade_disponiveis)

contratos_disponiveis = sorted(df['tipo_contratacao'].unique())
contratos_selecionados = st.sidebar.multiselect('Selecione o(s) tipo(s) de contrato:', contratos_disponiveis, default=contratos_disponiveis)

tamanho_disponiveis = sorted(df['porte_empresa'].unique())
tamanho_selecionado = st.sidebar.multiselect('Selecione o(s) tamanho(s) da empresa:', tamanho_disponiveis, default=tamanho_disponiveis)

df_filtrado = df[
    (df['ano_trabalho'].isin(anos_selecionados)) &
    (df['nivel_experiencia'].isin(senioridade_selecionada)) &
    (df['tipo_contratacao'].isin(contratos_selecionados)) &
    (df['porte_empresa'].isin(tamanho_selecionado)) 
]

st.title('📈 Salários na Área de Dados')
st.markdown("Análise de salários na área de dados - 📝 Use os filtros para explorar os dados.")

st.subheader('📊 Análise Grafico')

if not df_filtrado.empty:
    salario_medio = df_filtrado['salario_em_usd'].mean()
    salatrio_maximo = df_filtrado['salario_em_usd'].max()
    salario_minimo = df_filtrado['salario_em_usd'].min()
    pais_mais_bem_pago = df_filtrado.loc[df_filtrado['salario_em_usd'].idxmax(), 'residencia_funcionario']
else:
    salario_medio = 0
    salatrio_maximo = 0
    salario_minimo = 0
    cargo_mais_bem_pago = 'N/A'

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio (USD)", f"${salario_medio:,.2f}")
col2.metric("Salário Máximo (USD)", f"${salatrio_maximo:,.2f}")
col3.metric("Salário Mínimo (USD)", f"${salario_minimo:,.2f}")
col4.metric("Paises Com Os Maiores Salarios", pais_mais_bem_pago)

st.markdown("-" * 20)   

st.subheader('📈 Graficos')

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['salario_em_usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='salario_em_usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'salario_em_usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='salario_em_usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'salario_em_usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")



col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['percentual_remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_contratacao', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_contratacao',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5  
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        grafico_porte = px.histogram(
            df_filtrado,
            x='porte_empresa',
            title='Distribuição de porte das empresas',
            labels={'porte_empresa': 'Porte da Empresa', 'count': 'Quantidade'}
        )
        grafico_porte.update_layout(title_x=0.1)
        st.plotly_chart(grafico_porte, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição de porte das empresas.")


st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)