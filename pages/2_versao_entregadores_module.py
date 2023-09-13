# Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import re 
import streamlit as st
import warnings
from PIL import Image
from datetime import datetime
import folium
from streamlit_folium import folium_static

warnings.filterwarnings('ignore')

# =============================================
# FUNÇÕES
# =============================================

def top_delivers ( df, top_asc ):

    filtro = ['City', 'Delivery_person_ID', 'Time_taken(min)']

    df_aux = df.loc[:, filtro].groupby(['City', 'Delivery_person_ID']).max().sort_values(['City', 'Time_taken(min)'], ascending = top_asc).reset_index()

    df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian',:].head(10)
    df_aux2 = df_aux.loc[df_aux['City'] == 'Urban',:].head(10)
    df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban',:].head(10)

    df_aux4 = pd.concat( [df_aux1, df_aux2, df_aux3]).reset_index()

    return df_aux4

# Criando a função para Modularização do código
def clean_code ( df ):
    """ Esta função tem a responsabilidade de limpar o dataframe 

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados 
        3. Remoção dos espaços das variáveis de texto 
        4. Formatação da coluna de datas 
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe    
    """

    # Exclusão das linhas vazias ('NaN ') da idade dos entregadores na coluna 'Delivery_person_Age':
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # Excluindo as linhas vazias ('NaN ') da coluna 'multiples_deliveries':
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # Conversao de texto para numeros inteiros na coluna 'Delivery_person_Age':
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

    # Conversao de texto para numeros decimais na coluna 'Delivery_person_Ratings':
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

    # Conversao de texto para numeros inteiros na coluna 'multiple_deliveries':
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int) 

    # Conversao de texto para data na coluna 'Order_Date':
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')

    # Remocao dos espaços finais de todas as linhas das colunas através do STRIP(), sem utilização de LOOP FOR:
    df['ID'] = df.loc[:, 'ID'].str.strip()
    df['Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df['Road_traffic_density'] = df.loc[ : ,'Road_traffic_density'].str.strip()
    df['Type_of_order'] = df.loc[ : ,'Type_of_order'].str.strip()
    df['Type_of_vehicle'] = df.loc[ : ,'Type_of_vehicle'].str.strip()
    df['Festival'] = df.loc[ : ,'Festival'].str.strip()
    df['City'] = df.loc[ : ,'City'].str.strip()

    return df

# ============================================= INICIO ESTRUTURA LÓGICA DO CÓDIGO =============================================

# =============================================
# IMPORT DATASET
# =============================================

df_raw = pd.read_csv('train.csv')

# =============================================
# LIMPEZA DO BANCO DE DADOS 
# =============================================
# Iniciando a limpeza do Banco de Dados chamando a função criada para isso (clean_code)

df = clean_code ( df_raw )

# =============================================
# BARRA LATERAL NO STREAMLIT 
# =============================================

# Criando barra lateral no Streamlit com filtros

st.header('Marketplace - Visão Entregadores')

# Aplicando imagem de Logo na barra lateral 

#image_path = 'profile.png'
image = Image.open( 'profile.png' )
st.sidebar.image( image )

# Aplicando titulos na barra lateral 

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( 'Selecione uma data limite')

# Aplicando filtro de data com slider

date_slider = st.sidebar.slider( 
        'Até qual valor ?',
        value = datetime(2022, 4, 13),
        min_value = datetime(2022, 2, 11), 
        max_value = datetime(2022, 4, 6), 
        format = 'DD-MM-YYYY' )

st.sidebar.markdown( """---""" )

# Aplicando filtro de trafego com multiplos selects

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito', 
    ['Low', 'Medium', 'High', 'Jam'],
    default = 'Low')

st.sidebar.markdown( """---""" )
st.sidebar.markdown('### Powered by Comunidade DS')

# Linkando os filtros com os gráficos que contem DATA
filtro = df['Order_Date'] < date_slider
df = df.loc[ filtro, : ]

# Linkando os filtros com os gráficos que contem TRANSITO
filtro = df['Road_traffic_density'].isin( [traffic_options]) 
# .isin é utilizado para selecionar o que desejo selecionar e neste caso é o proprio filtro dentro do traffic_options

# =============================================
# LAYOUT NO STREAMLIT 
# =============================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap = 'Large')

        with col1:
            # Para a maior idade dos entregadores 
            st.subheader('Maior de idade')

            idade_maior = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior de idade', idade_maior)

        with col2:
            # Para a menor idade dos entregadores
            st.subheader('Menor de idade')

            idade_menor = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric( 'Menor de idade', idade_menor)

        with col3:
             # Para a melhor condição de veículos
            st.subheader('Melhor condição de veículos')
           
            melhor_condicao = df.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condição', melhor_condicao)

        with col4:
             # Para a pior condição de veículos
            st.subheader('Pior condição de veículos')
           
            pior_condicao = df.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição', pior_condicao)
    
    with st.container():
        st.markdown( """---""")
        st.title('Avaliações')

        col1, col2 = st.columns(2, gap = 'Large')

        with col1:
            # Para avaliação média por entregador
            st.markdown('##### Avaliações Médias por entregador')

            filtro = ['Delivery_person_ID', 'Delivery_person_Ratings']
            df_avg_ratings_per_deliver = df.loc[:, filtro].groupby('Delivery_person_ID').mean().reset_index()

            st.dataframe(df_avg_ratings_per_deliver)

        with col2:
            # Para a avaliação média por transito
            st.markdown('##### Avaliação média por transito')

            filtro = ['Road_traffic_density', 'Delivery_person_Ratings']
            df_aux = df.loc[:, filtro].groupby('Road_traffic_density').agg(['mean','std']).reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

            # Mudança de nomes das colinas do DataFrame auxiliar para 'Media' e 'Desvio_padrao'
            df_aux.columns = ['Road_traffic_density', 'Media', 'Desvio_padrao']

            st.dataframe(df_aux)

            # Para avaliação media por clima
            st.markdown('##### Avaliação média por clima')

            filtro = ['Weatherconditions', 'Delivery_person_Ratings']
            df_aux = df.loc[:, filtro].groupby('Weatherconditions').agg(['mean','std']).reset_index()
            df_aux = df_aux.loc[df_aux['Weatherconditions'] != 'conditions NaN', :]

            # Mudança de nomes das colunas do Data Frame auxiliar para 'Media'' e 'desvio_padrao'
            df_aux.columns = ['Weatherconditions', 'Media', 'Desvio_padrao']

            st.dataframe(df_aux)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')

        col1, col2 = st.columns(2, gap = 'Large')

        with col1:
            st.markdown('##### Top Entregadores mais rapidos')

            df_aux4 = top_delivers ( df, top_asc = True)
            st.dataframe(df_aux4)

        with col2:
            st.markdown('##### Top Entregadores mais lentos')

            df_aux4 = top_delivers ( df, top_asc = False)
            st.dataframe(df_aux4)



            

