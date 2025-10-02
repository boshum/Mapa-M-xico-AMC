# -*- coding: utf-8 -*-
"""
Created on Thu Oct  2 14:06:51 2025

@author: Mich
"""
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset

# Importamos los datos
df = pd.read_excel('C:/Users/Mich/Downloads/Membresia AMC 2025_filtrados.xlsx', sheet_name='Filtrados viven 2025')
mexico = gpd.read_file('C:/Users/Mich/Downloads/mexican-states/mexican-states/mexican-states.shp')

# Limpiamos los datos en blanco o N/D de la columna estado
df = df[df['Estado'] != '#N/A']
df = df[df['Estado'].notna()]
df = df[df['Sección'] != 'Internacional'] # y los datos internacionales

# Renombramos algunos datos de estados que no coinciden con los del mapa:
df['Estado'] = df['Estado'].str.replace('Coahuila', 'Coahuila de Zaragoza')
df['Estado'] = df['Estado'].str.replace('Veracruz', 'Veracruz de Ignacio de la Llave')
df['Estado'] = df['Estado'].str.replace('Michoacán', 'Michoacán de Ocampo')
df['Estado'] = df['Estado'].str.replace('Estado de México', 'México')

# Para procesar todas las áreas
areas = ['Agrociencias', 'Astronomía', 'Biología', 'Ciencias Sociales', 
         'Física', 'Humanidades', 'Ingeniería', 'Matemáticas', 'Medicina', 'Química']

#Creamos DataFrames para las diferentes áreas
for area in areas:
    df_area = df[df['Área'] == area]
    #si el DF no está vació crea Cuentas_EGA
    if len(df_area) > 0:
        #Contamos cuántos hombres y mujeres hay por estado (Estado-Género)
        Cuentas_EGA = df_area.groupby(['Estado', 'Género']).size().unstack(fill_value=0)
        
        # Si no hay valor en H o M, se rellena con 0
        if 'H' not in Cuentas_EGA.columns:
            Cuentas_EGA['H'] = 0
        if 'M' not in Cuentas_EGA.columns:
            Cuentas_EGA['M'] = 0
            
        Cuentas_EGA['Total'] = Cuentas_EGA.sum(axis=1) #se crea un total de H y M
        Cuentas_EGA = Cuentas_EGA.reset_index() #Volvemos a estado una columna
        
        mexico_data = mexico.merge(Cuentas_EGA, how='left', left_on='name', right_on='Estado')
        
        # Rellenar NaN con 0 si es necesario
        mexico_data['H'] = mexico_data['H'].fillna(0)
        mexico_data['M'] = mexico_data['M'].fillna(0)
        mexico_data['Total'] = mexico_data['Total'].fillna(0)
        
        # Crear mapa
        fig, ax = plt.subplots(1, 1, figsize=(25, 15))
        mexico_data.plot(column='Total', cmap='viridis_r', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
        
        # Solo mostrar etiquetas para estados con datos
        for idx, row in mexico_data.iterrows():
            central_states = ['México', 'Morelos', 'Ciudad de México']
            if row['Estado'] not in central_states:# Solo estados con miembros en esta área
                if row['Total'] > 0:  
                    plt.annotate(text=f"{row['Estado']}\nH: {int(row['H'])} M: {int(row['M'])}", 
                                 xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
                                 horizontalalignment='center', 
                                 verticalalignment='center', 
                                 fontsize=7,
                                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))
        
        plt.title(f'Distribución de Miembros de la AMC en {area} por Estado (2025)', fontsize=14) #título que cambia por área
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
        plt.savefig(f'Miembros_de_AMC_por_Estado_2025_{area}.png') #guardar mapas como png
        plt.show() #mostrar mapas