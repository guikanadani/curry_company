# Libraries
import pandas as pd
import plotly.express as px
import numpy as np
from haversine import haversine
import re 
import streamlit as st
import warnings
from PIL import Image
from datetime import datetime
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go

warnings.filterwarnings('ignore')

# =============================================
# FUNÇÕES
# =============================================

def avg_std_time_traffic( df ):

    filtro = ['Time_taken(min)', 'City', 'Road_traffic_density']
    df_aux = df.loc[:, filtro].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std']}).reset_index()
    df_aux.columns = ['City', 'Type_of_order', 'Media', 'Desv_pad']

    # Observamos novamente que há a presença de linhas vazias no banco, assim precisamos removelas
    linhas_vazias = df_aux['City'] != 'NaN'
    df_aux = df_aux.loc[linhas_vazias,:]

    return fig 

def avg_std_time_graph(df):
    filtro = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df['Distance'] = df.loc[:, filtro].apply( lambda x: haversine ( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)
        
    avg_distance = df.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()

    fig = go.Figure( data = [go.Pie( labels = avg_distance['City'], values = avg_distance['Distance'], pull=[ 0, 0.1, 0 ])])
    # Figure é uma nova biblioteca onde possui o destaque em gráficos (mais ressaltados), o pull é utilizado para salientar o grafico de pizza e o 0.1 é o quanto queremos destacar a mais do grafico
    
    return fig 

def avg_std_time_delivery( df, festival, op ):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega 
        Parâmetros: 
        Input: 
            - df: Dataframe com os dados necessários para o cálculo
            - op: Tipo de operação que precisa ser calculado
                'avg_time': Calcula o tempo médio 
                'std_time': Calcula o desvio padrão do tempo

        Output: 
            - df: Dataframe com 2 colunas e 1 linha
    """

    filtro = ['Time_taken(min)', 'Festival']
    df_aux = df.loc[:, filtro].groupby('Festival').agg( {'Time_taken(min)': ['mean', 'std']}).reset_index()
    df_aux.columns = ['Festival', 'Media', 'Desv_pad']
    # Observamos novamente que há a presença de linhas vazias no banco, assim precisamos removelas
    linhas_vazias = df_aux['Festival'] != 'NaN'
    df_aux = df_aux.loc[linhas_vazias,:]
    # Agora partimos para o filtro selecionando apenas o que teve entregas no FESTIVAL
    linha_selecionada = df_aux['Festival'] == festival
    df_aux = round(df_aux.loc[linha_selecionada, op],2)

    return df_aux

def distance( df, fig ):
    if fig == False:
        filtro = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df['Distance'] = df.loc[:, filtro].apply( lambda x: haversine ( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)
        avg_distance = round(df['Distance'].mean(),2)

        return avg_distance
    
    else:
        filtro = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df['Distance'] = df.loc[:, filtro].apply( lambda x: haversine ( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)
        avg_distance = df.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()
        fig = go.Figure( data = go.Pie( labels = avg_distance['City'], values = avg_distance['Distance'], pull = [0, 0.1, 0]))

        return fig 


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
    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype( int )

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

st.header('Marketplace - Visão Restaurantes')

# Aplicando imagem de Logo na barra lateral 

image_path = 'profile.png'
image = Image.open( image_path )
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with  tab1:
    with st.container():
        st.title( 'Overal Metrics' )

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:

            delivery_unique = df['Delivery_person_ID'].nunique()
            col1.metric( 'Entregadores Unicos', delivery_unique)

        with col2:
            avg_distance = distance (df, fig = False)
            col2.metric('A distancia media das entregas', avg_distance)        

        with col3:
            df_aux = avg_std_time_delivery (df, festival = 'Yes', op = 'Media')
            col3.metric( 'Tempo medio de Entregado c/ Festival', df_aux)

        with col4:
            df_aux = avg_std_time_delivery(df, festival = 'Yes', op = 'Desv_pad')
            col4.metric( 'Tempo medio de Entregado c/ Festival', df_aux)

        with col5:
            df_aux = avg_std_time_delivery(df, festival = 'No', op = 'Media')
            col5.metric( 'Tempo medio de Entregado c/ Festival', df_aux)

        with col6:
            df_aux = avg_std_time_delivery(df, festival = 'No', op = 'Desv_pad')
            col6.metric( 'Tempo medio de Entregado c/ Festival', df_aux)

    with st.container():
        st.markdown( '''---''')
        st.title( 'Tempo Medio de entrega por cidade' )

        filtro = ['City', 'Time_taken(min)']
        df_aux = df.loc[:, filtro].groupby('City').agg( {'Time_taken(min)': ['mean', 'std']}).reset_index()
        df_aux.columns = ['City','Media', 'Desv_pad']

        fig = go.Figure()
        fig.add_trace(go.Bar( name = 'Control', x = df_aux['City'], y = df_aux['Media'], error_y = dict ( type = 'data', array = df_aux['Desv_pad'])))
        # O error_y é o desvio padrao (barrinha) apresentada no proprio grafico de barras

        st.plotly_chart(fig)

    with st.container():
        st.markdown( '''---''')

        col1, col2 = st.columns(2)

        with col1:
            fig = avg_std_time_graph( df )
            st.plotly_chart(fig)

        with col2:

            filtro = ['Time_taken(min)', 'City', 'Type_of_order']
            df_aux = df.loc[:, filtro].groupby(['City', 'Type_of_order']).agg( {'Time_taken(min)': ['mean', 'std']}).reset_index()
            df_aux.columns = ['City', 'Type_of_order', 'Media', 'Desv_pad']

            # Observamos novamente que há a presença de linhas vazias no banco, assim precisamos removelas
            linhas_vazias = df_aux['City'] != 'NaN'
            df_aux = df_aux.loc[linhas_vazias,:]

            st.dataframe(df)
        

    with st.container():
        st.markdown( '''---''')
        st.title('Distribuição da Tempo')

        col1, col2 = st.columns(2)

        with col1:
            fig = distance (df, fig = True)
            st.plotly_chart(fig)

        with col2:
            fig = avg_std_time_traffic( df )
            st.plotly_chart(fig)

