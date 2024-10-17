import streamlit as st
import pandas as pd
import openpyxl
from datetime import date

#Setup de informações básicas
hoje = date.today()
inicio_mes = date(hoje.year, hoje.month, 1)

# Carregar dados da planilha Excel no Google Drive
file_path = 'rptDespesas.xlsx'
df = pd.read_excel(file_path)

# Garantir que a coluna de data está no formato datetime
df['Data Pgto.'] = pd.to_datetime(df['Data Pgto.'], errors='coerce')
df['Data'] = pd.to_datetime(df['Data Pgto.']).dt.date

#Configurações da Página
st.set_page_config(page_title="Dasboard AEAS - Despesas", page_icon="img/icon 100x100.png", layout="wide", initial_sidebar_state="expanded", menu_items={'Get Help': 'https://www.rcdourado.com'})

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)


# Configuração do título do dashboard
st.title('Dashboard Despesas')
st.divider()

# Filtros de busca
with st.sidebar:
    #st.sidebar.image("logo AEAS grayscale.png", width=80) 
    st.title("Filtro de Dados")
    st.divider()

data_inicio = st.sidebar.date_input("Data de Início", inicio_mes)
data_fim = st.sidebar.date_input("Data de Fim", hoje)
tipo = st.sidebar.selectbox("Filtrar por Tipo", options=["Todos"] + df['Tipo'].unique().tolist())
situacao = st.sidebar.selectbox("Filtrar por Situação", options=["Todos"] + df['Situação'].unique().tolist())
st.sidebar.divider()
parceiro = st.sidebar.selectbox("Buscar por Parceiro de Negócio", options=["Todos"] + df['Parceiro de Negócio'].unique().tolist())
#nrodoc = st.sidebar.text_input("Nro Documento")
st.sidebar.divider()

# Aplicação dos filtros
if parceiro != "Todos":
    df = df[df['Parceiro de Negócio'] == parceiro]

if data_inicio:
    df = df[df['Data Pgto.'] >= pd.to_datetime(data_inicio)]

if data_fim:
    df = df[df['Data Pgto.'] <= pd.to_datetime(data_fim)]

#if nrodoc:
#    df = df[df['Nº Doc.'].str.contains(nrodoc, case=False)]

if tipo != "Todos":
    df = df[df['Tipo'] == tipo]

if situacao != "Todos":
    df = df[df['Situação'] == situacao]

# Cálculo dos valores totais
total_pago = df[df['Situação'] == 'PAGO']['Valor'].sum()
total_em_atraso = df[df['Situação'] == 'EM ATRASO']['Valor'].sum()
total_pendente = df[df['Situação'] == 'PENDENTE']['Valor'].sum()

# Exibição dos cards com os valores totais na mesma linha
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Pago", value=f"R$ {total_pago:,.2f}")
with col2:
    st.metric(label="Total a Pagar", value=f"R$ {total_pendente:,.2f}")
with col3:
    st.metric(label="Total em Atraso", value=f"R$ {total_em_atraso:,.2f}")

st.divider()

# Exibir tabela filtrada
total_recebiveis = total_pago + total_em_atraso + total_pendente
col4, col5 = st.columns(2)
with col4:
    st.title("Pagamentos (total)")
with col5:
    st.metric(label="", value=f"R$ {(total_recebiveis):,.2f}")
# Dataframe completo
st.dataframe(df[['Data', 'Parceiro de Negócio', 'Tipo', 'Situação', 'Valor', 'Nº Doc.','Título']],hide_index=True)

# Gráficos
st.divider()
st.title("Pagamentos por Tipo (total)")
totais_por_tipo = df.groupby('Tipo')['Valor'].sum()
st.bar_chart(totais_por_tipo)

#Rodapé
st.divider()
st.text("Associação dos Engenheiros e Arquitetos de Sorocaba - Todos os direitos reservados.")
st.text("Dados de 01/01/2017 a 31/12/2024")