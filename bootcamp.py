import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import folium as fl
import plotly.graph_objects as go

from PIL import Image
from streamlit_folium import folium_static
from folium.plugins import FastMarkerCluster

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

image = Image.open('logo.png')
st.image(image, width=300)

#==================================
# Main Page
#==================================
st.markdown('## Dashbord de acompanhamento Airbnb')

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        price_mean = np.round(df1.loc[:,'price'].mean(),2)
        st.metric('Valor médio ($)', price_mean)

    with col2:
        price_max = '{:,}'.format(df1.loc[:,'price'].max()).replace(',','.')
        st.metric('Aluguel Mais Caro ($)', price_max)

    with col3:
        price_std = np.round(df1.loc[:,'price'].std(),2)
        st.metric('Std Dos Alugueis ($)', price_std)

with st.container():
    name = (df1.loc[:,['name','number_of_reviews','latitude','longitude','reviews_per_month', 'price']]
               .groupby(['name','latitude','longitude','number_of_reviews','price'])
               .max()
               .sort_values('number_of_reviews', ascending=False)
               .reset_index()
               .head(10))

    map = fl.Map()
    master_cluster = fl.plugins.MarkerCluster().add_to(map)

    for index, location_index in name.iterrows():
        latitude = location_index['latitude']
        longitude = location_index['longitude']

        pop_up = f'<div style="width: 250px;">' \
             f'Nome: {location_index["name"]} <br>' \
             f'Número de Avaliações: {location_index["number_of_reviews"]} <br>' \
             f'Preço: ${location_index["price"]:.2f} <br>' \
             f'</div>'
        

        fl.Marker([latitude,longitude], zoom_start=10, popup=pop_up).add_to(master_cluster)
    
    folium_static(map, width=864, height=486)

with st.container():
    grafic = np.round(df1.loc[:,['neighbourhood_group','price']].groupby('neighbourhood_group').mean().reset_index(),2)

    fig = px.bar(grafic, x='neighbourhood_group',y='price', text_auto=True, labels={'price':'Valor médio','neighbourhood_group':'Região'})
    st.plotly_chart(fig, use_container_width=True)
