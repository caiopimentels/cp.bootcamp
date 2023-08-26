import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import folium as fl

from PIL import Image
from streamlit_folium import folium_static

#================================
#Funções:
#================================
def clear_code(df1):
    df1 = df1[~df1['last_review'].isnull()]
    df1 = df1[~df1['name'].isnull()]
    df1 = df1[~df1['host_name'].isnull()]

    return df1

#-------------------------------- Inicio da Estrutura lógica do código --------------------------------
df = pd.read_csv('dataset/AB_NYC_2019.csv.zip')
df1 = df.copy()

df1 = clear_code(df1)

#==================================
# Barra Lateral Streamlit
#==================================
image = Image.open('logo.png')
st.sidebar.image(image, width=200)

st.sidebar.markdown('# Airbnb')
st.sidebar.markdown('### Pertença a qualquer lugar onde você estiver #')
st.sidebar.markdown("""---""")

neighborhood_unique = df1['neighbourhood_group'].unique()

neighborhood = st.sidebar.multiselect('Escolha os bairros que deseja filtrar',
                                neighborhood_unique,
                                default=neighborhood_unique)

selecao = df1['neighbourhood_group'].isin(neighborhood)
df1 = df1.loc[selecao,:]

#==================================
# Main Page
#==================================
st.markdown('## Dashbord de acompanhamento Airbnb')

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        price_mean = np.round(df1.loc[:,'price'].mean(),2)
        st.metric('Valor médio ($)', price_mean, help='Com base no filtro aplicador')

    with col2:
        price_max = '{:,}'.format(df1.loc[:,'price'].max()).replace(',','.')
        st.metric('Aluguel Mais Caro ($)', price_max, help='Com base no filtro aplicador')

    with col3:
        price_std = np.round(df1.loc[:,'price'].std(),2)
        st.metric('Std Dos Alugueis ($)', price_std, help='Com base no filtro aplicador')
    st.markdown("""---""")

with st.container():
    st.markdown('### Localização dos 10 melhores imóveis')
    name = (df1.loc[:,['name','number_of_reviews','latitude','longitude','reviews_per_month', 'price']]
               .groupby(['name','latitude','longitude','number_of_reviews','price'])
               .max()
               .sort_values('number_of_reviews', ascending=False)
               .reset_index()
               .head(10))

    map = fl.Map()
    #map.fit_bounds(map.get_bounds(), padding=(30, 30))
    
    master_cluster = fl.plugins.MarkerCluster().add_to(map)

    for index, location_index in name.iterrows():
        latitude = location_index['latitude']
        longitude = location_index['longitude']

        pop_up = f'<div style="width: 250px;">' \
             f'Nome: {location_index["name"]} <br>' \
             f'Número de Avaliações: {location_index["number_of_reviews"]} <br>' \
             f'Preço: ${location_index["price"]:.2f} <br>' \
             f'</div>'
        

        fl.Marker([latitude,longitude], zoom_start=5, popup=pop_up).add_to(master_cluster)
    
    
    folium_static(map, width=720, height=400)
    st.markdown("""---""")
    
with st.container():
    st.markdown('### Valor médio de aluguel por região')
    grafic = np.round(df1.loc[:,['neighbourhood_group','price']].groupby('neighbourhood_group').mean().reset_index(),2)

    fig = px.bar(grafic, x='neighbourhood_group',y='price', text_auto=True, labels={'price':'Valor médio','neighbourhood_group':'Região'})
    st.plotly_chart(fig, use_container_width=True)
