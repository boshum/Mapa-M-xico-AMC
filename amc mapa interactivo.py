# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 22:04:21 2025

@author: Mich
"""
# Importamos librerías para limpiar los datos y graficarlos
import pandas as pd
import geopandas as gpd
import plotly.express as px
import json


#Importamos los datos
df = pd.read_excel('C:/Users/Mich/Downloads/Membresia AMC 2025_filtrados.xlsx', sheet_name='Filtrados viven 2025')

#Limpiamos los datos en blanco o N/D de la columna estado
df = df[df['Estado'] != '#N/A']
df = df[df['Estado'].notna()]
df = df[df['Sección'] != 'Internacional']  #y los datos internacionales

#Renombramos algunos datos de estados que no coinciden con los del mapa:
#Coahuila 
df['Estado'] = df['Estado'].str.replace('Coahuila', 'Coahuila de Zaragoza')
df['Estado'] = df['Estado'].str.replace('Veracruz', 'Veracruz de Ignacio de la Llave')
df['Estado'] = df['Estado'].str.replace('Michoacán', 'Michoacán de Ocampo')
df['Estado'] = df['Estado'].str.replace('Estado de México', 'México')

#Contamos cuántos hombres y mujeres hay por estado (Estado-Género)
Cuentas_EG = df.groupby(['Estado', 'Género']).size().unstack(fill_value=0)
Cuentas_EG['Total'] = Cuentas_EG.sum(axis=1)
Cuentas_EG = Cuentas_EG.reset_index()

#Importamos el mapa de México en formato .shp
mexico = gpd.read_file('C:/Users/Mich/Downloads/mexican-states/mexican-states/mexican-states.shp')

#Unimos los datos de Cuentas EG y el mapa mexico, ya que los estados coinciden
mexico_data = mexico.merge(Cuentas_EG, how='left', left_on='name', right_on='Estado')

#Convertimos nuestro data frame a GeoJSON para que sea interactivo
mexico_data_geojson = json.loads(mexico_data.to_json())

#Creamos el mapa interactivo con choropleth
fig = px.choropleth_mapbox(mexico_data, #dataframe
                           geojson=mexico_data_geojson, #el dataframe convertido a geojson
                           locations=mexico_data.index, #ubicación del mapa que depende del df
                           color='Total', # color de los marcadores
                           color_continuous_scale='Viridis_r', #escala de colores para el mapa
                           mapbox_style="carto-positron", #estilo del mapa base
                           zoom=4, #zoom en el mapa para que se vea México
                           center={"lat": 23.6345, "lon": -102.5528}, #ubicación en el mapamundi para centrar México
                           opacity=0.7, #opacidad de los marcadores
                           hover_data={'H': True, 'M': True, 'Total': True, 'Estado': True}, #Data a mostrar en el mapa
                           labels={'Total': 'Total Miembros'}, #Etiquetas
                           title='Distribución de Miembros de la AMC por Estado (2025)' #Título del mapa
                          )

#Formato de la etiqueta flotante 
fig.update_traces(
    hovertemplate="<b>%{customdata[3]}</b><br>" +
                  "Total: %{z}<br>" +
                  "Hombres: %{customdata[0]}<br>" +
                  "Mujeres: %{customdata[1]}<extra></extra>"
)

# Formato del mapa
fig.update_layout(
    width=1000, #ancho del mapa
    height=800, #alto del mapa
    title_x=0.5 #ubicación del titulo
)

fig.show()

#Exportamos el mapa como html
fig.write_html("miembros_amc_por_estado_mapa.html")