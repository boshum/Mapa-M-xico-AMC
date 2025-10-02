# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 23:01:41 2025

@author: Mich
"""

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset


#Importamos los datos
df = pd.read_excel('C:/Users/Mich/Downloads/Membresia AMC 2025_filtrados.xlsx', sheet_name='Filtrados viven 2025')

#Limpiamos los datos en blanco o N/D de la columna estado
df = df[df['Estado'] != '#N/A']
df = df[df['Estado'].notna()]
df = df[df['Sección'] != 'Internacional'] #y los datos internacionales

#Renombramos algunos datos de estados que no coinciden con los del mapa:
#Coahuila 
df['Estado'] = df['Estado'].str.replace('Coahuila', 'Coahuila de Zaragoza')
#Veracruz
df['Estado'] = df['Estado'].str.replace('Veracruz', 'Veracruz de Ignacio de la Llave')
#Michoacan
df['Estado'] = df['Estado'].str.replace('Michoacán', 'Michoacán de Ocampo')
#Estado de México
df['Estado'] = df['Estado'].str.replace('Estado de México', 'México')


#Contamos cuántos hombres y mujeres hay por estado (Estado-Género)
Cuentas_EG = df.groupby(['Estado', 'Género']).size().unstack(fill_value=0)
Cuentas_EG['Total'] = Cuentas_EG.sum(axis=1)

#Volvemos a estado una columna
Cuentas_EG = Cuentas_EG.reset_index()


#Importamos el mapa de México en formato .shp
mexico = gpd.read_file('C:/Users/Mich/Downloads/mexican-states/mexican-states/mexican-states.shp')

#Unimos los datos de Cuentas EG y el mapa mexico, ya que los estados coinciden
mexico_data = mexico.merge(Cuentas_EG, how='left', left_on='name', right_on='Estado')
#mexico_data = mexico.merge(Cuentas_EGA_agro, how='left', left_on='name', right_on='Estado')

#Realizamos el mapa 
fig, ax = plt.subplots(1, 1, figsize=(27, 18))
mexico_data.plot(column='Total', cmap='viridis_r', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)

# Añadimos las etiquetas al mapa principal (only for states with fewer neighbors)
for idx, row in mexico_data.iterrows():
    #Algunos estados estaban muy juntos así que se decidió hacer un mapa dentro del mapa
    centro = ['México', 'Morelos', 'Tlaxcala', 'Puebla', 'Ciudad de México', 'Querétaro', 'Hidalgo']
    if row['Estado'] not in centro: #condicional para mostrar las etiquetas de los estados que no están en centro
        plt.annotate(text=f"{row['Estado']}\nH: {row['H']} M: {row['M']}", #datos de las etiquetas
                     xy=(row['geometry'].centroid.x, row['geometry'].centroid.y), #posicionamiento de las etiquetas en el mapa
                     horizontalalignment='left', #alineación horizontal
                     verticalalignment='bottom', fontsize=11, # alineación vertical y tamaño de letra
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.5)) # características de la caja contenedora del texto
plt.title('Distribución de Miembros de la AMC por Estado (2025)') #título 
plt.axis('off') #para que no se muestren líneas de ejes

#Creamos el axis dentro del mapa
ax_dentro = zoomed_inset_axes(ax, zoom=3, loc='upper right')  #Zoom en el área y ubicación del mapa
mexico_data.plot(column='Total', cmap='viridis_r', linewidth=0.8, ax=ax_dentro, edgecolor='0.8') #características del mapa

#Colocamos los límites del mapa del centro
limi_centro = [-100.5, -97.5, 18.5, 21]  # [xmin, xmax, ymin, ymax]
ax_dentro.set_xlim(limi_centro[0], limi_centro[1]) #limi_centro[0] = -100.5, limi_centro[1] = -97.5
ax_dentro.set_ylim(limi_centro[2], limi_centro[3]) #limi_centro[3] = 18.5, limi_centro[4] = 21

# Añadimos etiquetas al mapa del centro
for idx, row in mexico_data.iterrows():
    centroid_x = row['geometry'].centroid.x
    centroid_y = row['geometry'].centroid.y
    #Sólo añadimos la etiquetas de los estados en el área limitada que creamos
    if (limi_centro[0] <= centroid_x <= limi_centro[1] and 
        limi_centro[2] <= centroid_y <= limi_centro[3]):
        ax_dentro.annotate(text=f"{row['Estado']}\nH: {row['H']} M: {row['M']}", #mismo código que usamos para el mapa grande
                         xy=(centroid_x, centroid_y),
                         horizontalalignment='center', 
                         verticalalignment='center', fontsize=8,
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.5))

ax_dentro.set_title('Región Central', fontsize=12) #título del mapa de adentro

plt.axis('off') #sin ejes 
plt.tight_layout() #para separar un poco más
plt.savefig('Miembros_de_AMC_por_Estado_2025.png') #guardar el mapa.png
plt.show() #mostrar el mapa