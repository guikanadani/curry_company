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

def country_maps( df ):
    filtro = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = df.loc[:, filtro].groupby(['City', 'Road_traffic_density']).median().reset_index()

    # Novamente observamos ao plotar o Data Frame auxiliar que temos diversar linhas sem valor ('NaN') e precisamos realizar tal limpeza 
    # Assim o faremos dentro deste mesmo exercicio, mas como 'mundo real' devemos destinar tal limpeza em uma area especifica, como no primeiro topido deste projeto
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    # Criação do gráfico de MAPA:
    # Para a criação do grafico de MAPA vamos utilizar uma nova biblioteca chama da FOLIUM e para isso devemos instalala no terminal utilizando --pip install folium
    # Assim apos a instalação vamos importala para o codigo

    map = folium.Map() #Este comando proprio da biblioteca dispoem um mapa global para visualização

    # folium.Marker( [latitude, longitude]).add_to() Comando para adicição de marcador dentro do MAPA, assim precisamos substitutir a LAT e LONG 
    # folium.Marker(df_aux.loc[0, 'Delivery_person_latitude'], df_aux.loc[0, 'Delivery_person_longitude']).add_top (map) 
    # ao realizar somente este comando a mapa ira dispor somente de um pino
    # para isso preciso realizar o LOOP FOR dentro da lista

    for index, location_info in df_aux.iterrows(): # utilização do iterrows para criar um objeto de iteração pois devido a biblioteca 
        folium.Marker([location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup = location_info[['City','Road_traffic_density']]).add_to(map) # o comando POPUP serve justamente para adicionar um POPUP dentro do mapa com as informações que 
                                                                                            # desejo mostrar ao usuario

    # Plot do mapa para visualização
    folium_static( map, width = 1024, height = 600 )

def order_share_by_week( df ):
        
    filtro1 = ['ID', 'week_of_year']
    df_aux1 = df.loc[:, filtro1].groupby('week_of_year').count().reset_index()

    # Agora vamos realizar a contagem de entregadores unicos por semana
    filtro2 = ['Delivery_person_ID', 'week_of_year']
    df_aux2 = df.loc[:, filtro2].groupby('week_of_year').nunique().reset_index() # Utilizando .nunique() para contagem de valores unicos da coluna

    # Neste exercicio criamos dois Data Frames com filtros e valores diferentes e agora precisamos fazer a uniao desses DataFrames
    # Para isso vamos usar a tecnica de SQL para esta junção onde vamo mergir uma mesma coluna em comum desses Data Frames
    df_aux = pd.merge(df_aux1, df_aux2, how = 'inner') # O HOW é utilizado justamente do COMO sera a junção dos dois DF, e o inner é a função SQL para junção

    #df_aux # Com esse novo Data Frame temos a junção dos dois unidos pelo 'week_of_year'

    # Partimos agora para a resolução final deste exercicio onde sera necessario criar uma coluna para demonstrar os valores de entregas por quantidade unica de entregadores

    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x = 'week_of_year', y = 'order_by_deliver')

    return fig

def order_by_week( df ):
    df['week_of_year'] = df['Order_Date'].dt.strftime( '%U' )

    filtro = ['ID', 'week_of_year']

    df_aux = df.loc[:, filtro].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x = 'week_of_year', y = 'ID')

    return fig

# Função para receber um DF e gerar um gráfico de pizza 
def traffic_order_city( df ):
    filtro = ['ID', 'City', 'Road_traffic_density']

    df_aux = df.loc[:, filtro].groupby(['City','Road_traffic_density']).count().reset_index()

    # Observamos no Data Frame auxiliar gerado que novamente temos a presença de linhas vazias e precisamos fazer a limpeza do banco de dados
    # Podemos realizar esta limpeza junto a LIMPEZA DO BANCO DE DADOS no primeiro topico ou diretamente aqui neste Data Frame auxiliar
    # Vamos realizar a limpeza aqui mesmo tanto da coluna 'City' quando da 'Road_traffic_density'
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    
    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')

    return fig 

# Função para receber um DF e gerar um gráfico de pizza com filtro diferente
def traffic_order_share( df ):
    filtro = ['ID', 'Road_traffic_density']

    df_aux = df.loc[:, filtro].groupby('Road_traffic_density').count().reset_index()

    # Criando uma nova coluna para porcentagem 
    # Realizando o calculo de porcentagem pegando a somatoria de cada densidade de trafego e dividindo pela somatoria total utilizando .sum()
    df_aux['entregas_perc'] = df_aux['ID'] / (df_aux['ID'].sum())

    # Ao visualizar o Data Frame df_aux, percebemos a presença de celular vazias ('NaN '), assim temos que exclui-las para melhor limpeza do banco
    # Esta limpeza pode ser feita novamente no topico de LIMPEZA DO BANCO DE DADOS ou entao aqui mesmo nesta seleção, vejamos:
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    
    fig = px.pie( df_aux, values = 'entregas_perc', names = 'Road_traffic_density')

    return fig 

# Função para receber um DF e gerar um gráfico de Barras
def order_metric( df ):

    filtro = ['ID', 'Order_Date']

    df_aux = df.loc[:, filtro].groupby('Order_Date').count().reset_index()

    # Utilizando a biblioteca PLOTLY porem no Streamlit não aceita o index px, deve ser adicionado uma propria função dele 
    # Criando o gráfico de BARRAS:

    fig = px.bar( df_aux, x = 'Order_Date', y = 'ID')

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

st.header('Marketplace - Visão Empresa')

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

# Criando ABAS no Streamlit 
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

# Para incluir itens e demais coisas dentro de cada ABA devemos usar o WITH,
# assim tudo o que estiver identado (com tab) estara dentro da ABA

with tab1:
    with st.container():
        # Order Metric - Visao Empresa
        fig = order_metric( df )
        
        st.markdown('# Orders by Day')
        st.plotly_chart (fig, user_container_width = True)

    with st.container():
        # Separando a ABA em duas colunas para implementos de dois gráficos
        col1, col2 = st.columns (2) # 2 de duas colunas

        # Adicionando intes e graficos dentro das colunas 
        with col1:
            fig = traffic_order_share( df )

            st.header('# Traffic Order Share')
            st.plotly_chart(fig, use_container_width = True)
           
        with col2:
            fig = traffic_order_city( df ) 

            st.header('Traffic Order City')
            st.plotly_chart(fig, use_container_width = True)

with tab2:
    with st.container():
        fig = order_by_week( df )

        st.markdown('# Order by Week')
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        st.markdown( '# Order Share by Week')
        # Criando o gráfico de LINHAS:
        st.plotly_chart(fig, use_container_width = True)
                    
with tab3:
    st.markdown( '# Country Maps')
    country_maps (df)
