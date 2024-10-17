import streamlit as st
import pandas as pd
import openpyxl
from datetime import date

#Setup de informações básicas
hoje = date.today()
inicio_mes = date(hoje.year, hoje.month, 1)

# Carregar dados da planilha Excel no Google Drive
file_path = 'rptReceitas.xlsx'
df = pd.read_excel(file_path)

# Garantir que a coluna de data está no formato datetime
df['Data Rec.'] = pd.to_datetime(df['Data Rec.'], errors='coerce')
df['Data'] = pd.to_datetime(df['Data Rec.']).dt.date

#Configurações da Página
st.set_page_config(page_title="Dasboard AEAS", page_icon="img/icon 100x100.png", layout="wide", initial_sidebar_state="expanded", menu_items={'Get Help': 'https://www.rcdourado.com'})

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)


# Configuração do título do dashboard
st.title('Dashboard Receitas')
st.divider()

# Filtros de busca
with st.sidebar:
    st.title("Filtro de Dados")
#    st.page_link("dashboard_aeas_nav.py", label="Voltar para Página Inicial", icon="🏠")
#    st.page_link("pages/dashboard_aeas_despesas.py", label="Ir para Página de Despesas", icon="🏠")
    st.divider()

data_inicio = st.sidebar.date_input("Data de Início", inicio_mes)
data_fim = st.sidebar.date_input("Data de Fim", hoje)
tipo = st.sidebar.selectbox("Filtrar por Tipo", options=["Todos"] + df['Tipo'].unique().tolist())
situacao = st.sidebar.selectbox("Filtrar por Situação", options=["Todos"] + df['Situação'].unique().tolist())
st.sidebar.divider()
parceiro = st.sidebar.selectbox("Buscar por Parceiro de Negócio", options=["Todos"] + df['Parceiro de Negócio'].unique().tolist())
st.sidebar.divider()

# Aplicação dos filtros
if parceiro != "Todos":
    df = df[df['Parceiro de Negócio'] == parceiro]

if data_inicio:
    df = df[df['Data Rec.'] >= pd.to_datetime(data_inicio)]

if data_fim:
    df = df[df['Data Rec.'] <= pd.to_datetime(data_fim)]

if tipo != "Todos":
    df = df[df['Tipo'] == tipo]

if situacao != "Todos":
    df = df[df['Situação'] == situacao]


# Dataframes com os boletos reemitidos separados R = Reemitidos T = total sem reemitidos
dfR = df[df['Nº Doc.'].str.endswith("R", na=False)]
dfT=df[~df.isin(dfR)].dropna(how = 'all')

# Cálculo dos valores totais
total_recebido = df[df['Situação'] == 'PAGO']['Valor'].sum()
total_recebido_sem_reemitidos = dfT[dfT['Situação'] == 'PAGO']['Valor'].sum()
total_em_atraso_sem_reemitidos = dfT[dfT['Situação'] == 'EM ATRASO']['Valor'].sum()
total_pendente_sem_reemitidos = dfT[dfT['Situação'] == 'PENDENTE']['Valor'].sum()
total_recebido_reemitidos = dfR[dfR['Situação'] == 'PAGO']['Valor'].sum()
total_em_atraso_reemitidos = dfR[dfR['Situação'] == 'EM ATRASO']['Valor'].sum()
total_pendente_reemitidos = dfR[dfR['Situação'] == 'PENDENTE']['Valor'].sum()
total_a_receber = df[df['Situação'] == 'EM ATRASO']['Valor'].sum() + df[df['Situação'] == 'PENDENTE']['Valor'].sum()


# Exibição dos cards com os valores totais na mesma linha
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Recebido", value=f"R$ {total_recebido:,.2f}")
with col2:
    st.metric(label="Total a Receber", value=f"R$ {total_pendente_sem_reemitidos + total_pendente_reemitidos:,.2f}")
with col3:
    st.metric(label="Total em Atraso", value=f"R$ {total_em_atraso_sem_reemitidos + total_em_atraso_reemitidos:,.2f}")

st.divider()

# Exibir tabela filtrada
total_recebiveis = total_recebido_sem_reemitidos + total_em_atraso_sem_reemitidos + total_pendente_sem_reemitidos
col4, col5 = st.columns(2)
with col4:
    st.title("Recebíveis")
    st.text("não considerando boletos reemitidos")
with col5:
    st.metric(label="", value=f"R$ {(total_recebiveis):,.2f}")

# Excluindo terminados com R
st.dataframe(dfT[['Data', 'Parceiro de Negócio', 'Tipo', 'Situação', 'Valor', 'Nº Doc.','Título']],hide_index=True)

# Exibir boletos reemitidos
st.divider()
col6, col7 = st.columns(2)
with col6:
    st.title("Boletos Reemitidos")
with col7:
    st.metric(label="", value=f"R$ {(total_recebido_reemitidos+total_em_atraso_reemitidos+total_pendente_reemitidos):,.2f}")
st.dataframe(dfR[['Data', 'Parceiro de Negócio', 'Tipo', 'Situação', 'Valor', 'Nº Doc.','Título']],hide_index=True)

# Gráficos
st.divider()
st.title("Recebíveis por Tipo (total)")
totais_por_tipo = df.groupby('Tipo')['Valor'].sum()
st.bar_chart(totais_por_tipo)

#Rodapé
st.divider()
st.text("Associação dos Engenheiros e Arquitetos de Sorocaba - Todos os direitos reservados.")
st.text("Dados de 01/01/2017 a 31/12/2024")