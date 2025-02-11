# app resultado de ações
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import timedelta

st.write("""
### O gráfico abaixo representa a evolução do preço ao longo dos anos
""") #estilo markdown para texto

st.sidebar.write("Filtros")

@st.cache_data # decorator para armazenar em cache
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    precos_acao = dados_acao.history(period='1d', start='2010-01-01', end='2024-12-31')
  #  print(precos_acao) 
    # precos_acao = pd.read_csv("BaseItau.csv")
    # precos_acao["Date"] = pd.to_datetime(precos_acao["Date"])
    # precos_acao = precos_acao.set_index("Date")
    #precos_acao = precos_acao[["Close"]]
    precos_acao = precos_acao["Close"]  # pega somente a coluna Close
    return precos_acao

#acoes = ["ITUB4.SA", "PETR4.SA", "VALE3.SA", "BBDC4.SA", "ABEV3.SA"]
#recuperando os tickers da Bolsa de Valores : https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-amplos/indice-ibovespa-ibovespa-composicao-da-carteira.htm
@st.cache_data # decorator para armazenar em cache
def carregar_tickers_acoes():
    base_tickers = pd.read_csv("IBOV.csv", sep=";") # , encoding='latin-1'
 #   print("============BASE DE DADOS.")
 #   print(base_tickers)
    tickers = list(base_tickers["Codigo"])
    tickers = [ticker + ".SA" for ticker in tickers]
    return tickers

acoes = carregar_tickers_acoes()
#print("============TICKERS.")
#print(acoes)

dados  = carregar_dados(acoes)
#print("============AÇÕES.")
#print(dados)

#prepara a lista de acoes para filtragem
lista_acoes = st.sidebar.multiselect("Selecione as ações para visualizar", dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: "Close"})

#filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider("Selecione o intervalo de datas", min_value=data_inicial, max_value=data_final, value=(data_inicial, data_final), step=timedelta(days=1))

#filtra os dados
dados = dados.loc[intervalo_data[0]:intervalo_data[1]]
#plota o grafico
grafico = st.line_chart(dados)

#performance dos ativos
texto_performance_ativos = ""

if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)  
elif len(lista_acoes) == 1:
    dados = dados.rename(columns={"Close": acao_unica})
         
#calcula a performance da carteira
carteira = [1000 for acao in lista_acoes]   #considerando que investiu 1000 em cada ação      
total_inicial_carteira = sum(carteira)
             
for i, acao in enumerate(lista_acoes):
    preco_inicial = dados[acao].iloc[0]
    preco_final = dados[acao].iloc[-1]
    if preco_inicial > 0:
        performance = float(preco_final/preco_inicial -1)
    else:
        performance = 0
    
    carteira[i] = carteira[i] * (1 + performance)   
    
    #acrescentando cores :cor[texto]    
    if performance > 0:
        texto_performance_ativos += f"  \n{acao}: :green[{performance:.1%}]"
    elif performance < 0:
        texto_performance_ativos += f"  \n{acao}: :red[{performance:.1%}]"
    else:        
        texto_performance_ativos += f"  \n{acao}: {performance:.1%}"

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira/total_inicial_carteira - 1
if performance_carteira > 0:
    texto_performance_ativos += f"  \n  \nDesempenho da Carteira: :green[{performance_carteira:.1%}]"
elif performance_carteira < 0:
    texto_performance_ativos += f"  \n  \nDesempenho da Carteira: :red[{performance_carteira:.1%}]"  
else:
    texto_performance_ativos += f"  \n  \nDesempenho da Carteira: {performance_carteira:.1%}"  

st.write(f"""
### Performance dos Ativos
Essa foi a performance dos ativos selecionados:

{texto_performance_ativos}
""") #estilo markdown para texto
