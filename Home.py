import streamlit as st
import pandas as pd
import openpyxl
from datetime import date

#Setup de informações básicas
hoje = date.today()
inicio_mes = date(hoje.year, hoje.month, 1)

# Carregar dados da planilha Excel no Google Drive
df_receitas = pd.read_excel('rptReceitas.xlsx')
df_despesas = pd.read_excel('rptDespesas.xlsx')
df_saldo = pd.read_excel('saldoSicredi.xlsx')

# Garantir que a coluna de data está no formato datetime
df_receitas['Data Rec.'] = pd.to_datetime(df_receitas['Data Rec.'], errors='coerce')
df_receitas['Data'] = pd.to_datetime(df_receitas['Data Rec.']).dt.date
df_despesas['Data Pgto.'] = pd.to_datetime(df_despesas['Data Pgto.'], errors='coerce')
df_despesas['Data'] = pd.to_datetime(df_despesas['Data Pgto.']).dt.date

#Configurações da Página
st.set_page_config(page_title="Dasboard AEAS", page_icon="img/icon 100x100.png", layout="wide", initial_sidebar_state="collapsed", menu_items={'Get Help': 'https://www.rcdourado.com'})

#         section[data-testid="stSidebar"][aria-expanded="true"]{display: none;}
hide_default_format = """
       <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Filtros de busca
with st.sidebar:
    st.title("Filtro de Dados")
    st.divider()

data_inicio = st.sidebar.date_input("Data de Início", inicio_mes)
data_fim = st.sidebar.date_input("Data de Fim", hoje)
tipo = st.sidebar.selectbox("Filtrar por Tipo", options=["Todos"] + df_receitas['Tipo'].unique().tolist())

# Aplicação dos filtros
if data_inicio:
    df_receitas = df_receitas[df_receitas['Data Rec.'] >= pd.to_datetime(data_inicio)]
    df_despesas = df_despesas[df_despesas['Data Pgto.'] >= pd.to_datetime(data_inicio)]

if data_fim:
    df_receitas = df_receitas[df_receitas['Data Rec.'] <= pd.to_datetime(data_fim)]
    df_despesas = df_despesas[df_despesas['Data Pgto.'] <= pd.to_datetime(data_fim)]

if tipo != "Todos":
    df_receitas = df_receitas[df_receitas['Tipo'] == tipo]
    df_despesas = df_despesas[df_despesas['Tipo'] == tipo]


##############################################
# MANIPULACAO DOS DFs
##############################################
# Dataframes com os boletos reemitidos separados R = Reemitidos T = total sem reemitidos
dfR = df_receitas[df_receitas['Nº Doc.'].str.endswith("R", na=False)]
dfT=df_receitas[~df_receitas.isin(dfR)].dropna(how = 'all')

# Cálculo dos valores totais RECEITAS
total_recebido = df_receitas[df_receitas['Situação'] == 'PAGO']['Valor'].sum()
total_recebido_sem_reemitidos = dfT[dfT['Situação'] == 'PAGO']['Valor'].sum()
total_em_atraso_sem_reemitidos = dfT[dfT['Situação'] == 'EM ATRASO']['Valor'].sum()
total_pendente_sem_reemitidos = dfT[dfT['Situação'] == 'PENDENTE']['Valor'].sum()
total_recebido_reemitidos = dfR[dfR['Situação'] == 'PAGO']['Valor'].sum()
total_em_atraso_reemitidos = dfR[dfR['Situação'] == 'EM ATRASO']['Valor'].sum()
total_pendente_reemitidos = dfR[dfR['Situação'] == 'PENDENTE']['Valor'].sum()
total_a_receber = df_receitas[df_receitas['Situação'] == 'EM ATRASO']['Valor'].sum() + df_receitas[df_receitas['Situação'] == 'PENDENTE']['Valor'].sum()

# Cálculo dos valores totais DESPESAS
total_pago = df_despesas[df_despesas['Situação'] == 'PAGO']['Valor'].sum()
total_em_atraso = df_despesas[df_despesas['Situação'] == 'EM ATRASO']['Valor'].sum()
total_pendente = df_despesas[df_despesas['Situação'] == 'PENDENTE']['Valor'].sum()

# Cálculos adicionais
saldo_sicredi = df_saldo['Saldo'].sum()
saldo_operacional = total_recebido - total_pago


##############################################
# RESUMO
##############################################

#st.image("img/Logo AEAS transp.png", width=150)
colA, colB, colC = st.columns(3)
with colA:
    st.title("Resumo Financeiro")
with colB:
    pass
with colC:
    st.metric(label="Saldo Sicredi Hoje", value=f"R$ {saldo_sicredi:,.2f}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total de Entradas", value=f"R$ {total_recebido:,.2f}")
with col2:
    st.metric(label="Total de Saídas", value=f"R$ {total_pago:,.2f}")
with col3:
    st.metric(label="Saldo Operacional", value=f"R$ {saldo_operacional:,.2f}")

st.divider()
st.divider()

##############################################
# RECEITAS
##############################################

# Exibição dos resultados RECEITAS
col1, col2, col3 = st.columns(3)
with col1:
    st.title("Receitas")
    st.page_link("pages/Receitas.py", label="Ver Detalhes das Receitas")
with col2:
    st.metric(label="Total Recebido", value=f"R$ {total_recebido:,.2f}")
with col3:
    st.metric(label="Total a Receber", value=f"R$ {total_a_receber:,.2f}")
st.divider()

st.subheader("Boletos Emitidos")   
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Recebido", value=f"R$ {total_recebido_sem_reemitidos:,.2f}")
with col2:
    st.metric(label="A Receber", value=f"R$ {total_pendente_sem_reemitidos:,.2f}")
with col3:
    st.metric(label="Em Atraso", value=f"R$ {total_em_atraso_sem_reemitidos:,.2f}")

st.subheader("Boletos Reemitidos")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Recebido", value=f"R$ {total_recebido_reemitidos:,.2f}")
with col2:
    st.metric(label="A Receber", value=f"R$ {total_pendente_reemitidos:,.2f}")
with col3:
    st.metric(label="Em Atraso", value=f"R$ {total_em_atraso_reemitidos:,.2f}")

# Gráficos
#st.divider()

#st.subheader("Gráfico de Recebíveis")
#st.text("em desenvolvimento, disponível em breve")
#st.line_chart(df_receitas, x="Data Rec.", y="Valor")

st.divider()

##############################################
# DESPESAS
##############################################

# Exibição dos resultados DESPESAS
st.title("Despesas")
st.page_link("pages/Despesas.py", label="Ver Detalhes das Despesas")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Pago", value=f"R$ {total_pago:,.2f}")
with col2:
    st.metric(label="Total a Pagar", value=f"R$ {total_pendente:,.2f}")
with col3:
    st.metric(label="Total em Atraso", value=f"R$ {total_em_atraso:,.2f}")

# Gráficos
st.divider()

#st.subheader("Gráfico das Despesas")
#st.text("em desenvolvimento, disponível em breve")
#st.line_chart(df_despesas, x="Data Pgto.", y="Valor")

#Rodapé
st.divider()
st.text("Associação dos Engenheiros e Arquitetos de Sorocaba - Todos os direitos reservados.")
st.text("Dados de 01/01/2017 a 31/12/2024")
