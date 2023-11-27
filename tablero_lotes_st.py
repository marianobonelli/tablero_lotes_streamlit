# Importar bibliotecas para manipulación de datos
import pandas as pd
import geopandas as gpd
from shapely import wkt

# Importar bibliotecas para visualización
import plotly.express as px
import plotly.graph_objs as go
import folium
from folium import FeatureGroup, LayerControl
from folium.plugins import HeatMap

# Importar bibliotecas para integración web y Streamlit
import streamlit as st
from streamlit_folium import folium_static

# Importar bibliotecas para manejo de imágenes
from PIL import Image

# Importar módulos o paquetes locales
from helper import translate


#####################   API   #####################

# Read the CSV file into a DataFrame
filtered_df = pd.read_csv('csv_rindes.csv')
user_info = {'email': "mbonelli@geoagro.com", 'language': 'es', 'env': 'prod', 'domainId': None, 'areaId': None, 'workspaceId': None, 'seasonId': None, 'farmId': None}
marca_blanca = 'assets/prodas.png'

##################### USER INFO #####################

language = user_info['language']
email = user_info['email']
env = user_info['env']
st.session_state['env'] = env

############################################################################
# Estilo
############################################################################

# Cargar la imagen
page_icon = Image.open("assets/favicon geoagro nuevo-13.png")

st.set_page_config(
    page_title="Tablero de Rindes",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

##################### LANGUAGE  #####################

c_1, c_2, c_3 = st.columns([1.5, 4.5, 1], gap="small")

with c_1:
    image_mb = Image.open(marca_blanca)
    # image_mb = image_mb.resize((220, 35))
    st.image(image_mb)

with c_3:   
    try:
        langs = ['es', 'en', 'pt']
        if language is not None:
            lang = st.selectbox(translate("language", language), label_visibility="hidden", options=langs, index=langs.index(language))
        else:  # from public link
            lang = st.selectbox(translate("es", language), label_visibility="hidden", options=langs)
        
        st.session_state['lang'] = lang
    except Exception as exception:
        lang = "es"
        st.session_state['lang'] = lang
        pass



##################### Titulo / solicitado por  #####################

st.subheader(translate("title",lang), anchor=False)
st.markdown(f'{translate("requested_by",lang)}<a style="color:blue;font-size:18px;">{""+email+""}</a> | <a style="color:blue;font-size:16px;" target="_self" href="/"> {translate("logout",lang)}</a>', unsafe_allow_html=True)


with st.sidebar:
    ############################################################################
    # Selector de color
    ############################################################################

    # Obtener la lista de rampas de colores cualitativos
    color_ramps = dir(px.colors.qualitative)
    # Filtrar los elementos que no son rampas de colores
    color_ramps = [ramp for ramp in color_ramps if not ramp.startswith("__")]
    # Encontrar el índice de 'T10' en la lista de rampas de colores
    default_index = color_ramps.index('T10') if 'T10' in color_ramps else 0

    # Selector para la rampa de colores con un valor predeterminado
    selected_color_ramp = st.selectbox(translate("color_palette", lang), color_ramps, index=default_index)

    # Usa getattr para obtener la rampa de colores seleccionada
    selected_colors = getattr(px.colors.qualitative, selected_color_ramp)

    ############################################################################
    # Area
    ############################################################################

    areas = sorted(filtered_df['area_name'].unique().tolist())

    container = st.container()
    select_all_areas = st.toggle(translate("select_all", lang), key='select_all_areas')

    if select_all_areas:
        selector_areas = container.multiselect(
            translate("area", lang),
            areas,
            areas)  # Todos los workspaces están seleccionados por defecto
    else:
        selector_areas = container.multiselect(
            translate("area", lang),
            areas,
            placeholder=translate("choose_option", lang)) 

    ############################################################################
    # Workspace
    ############################################################################

    # Filtra el DataFrame basado en las áreas seleccionadas
    filtered_df = filtered_df[filtered_df['area_name'].isin(selector_areas)]

    # Obtén los nombres de los workspaces únicos del DataFrame filtrado
    workspaces = sorted(filtered_df['workspace_name'].unique().tolist())

    container = st.container()
    select_all = st.toggle(translate("select_all", lang))

    if select_all:
        selector_workspaces = container.multiselect(
            translate("workspace", lang),
            workspaces,
            workspaces)  # Todos los workspaces están seleccionados por defecto
    else:
        selector_workspaces = container.multiselect(
            translate("workspace", lang),
            workspaces,
            placeholder=translate("choose_option", lang))

    ############################################################################
    # Season
    ############################################################################

    # Filtra el DataFrame basado en las áreas seleccionadas
    filtered_df = filtered_df[filtered_df['workspace_name'].isin(selector_workspaces)]

    # Obtén los nombres de los workspaces únicos del DataFrame filtrado
    seasons = sorted(filtered_df['season_name'].unique().tolist())

    container = st.container()
    select_all_seasons = st.toggle(translate("select_all", lang), key='select_all_seasons')

    if select_all_seasons:
        selector_seasons = container.multiselect(
            translate("season", lang),
            seasons,
            seasons)  # Todos los workspaces están seleccionados por defecto
    else:
        selector_seasons = container.multiselect(
            translate("season", lang),
            seasons,
            placeholder=translate("choose_option", lang)) 

    ############################################################################
    # Farm
    ############################################################################

    # Filtra el DataFrame basado en las áreas seleccionadas
    filtered_df = filtered_df[filtered_df['season_name'].isin(selector_seasons)]

    # Obtén los nombres de los workspaces únicos del DataFrame filtrado
    farms = sorted(filtered_df['farm_name'].unique().tolist())

    container = st.container()
    select_all_farms = st.toggle(translate("select_all", lang), key='select_all_farms')

    if select_all_farms:
        selector_farms = container.multiselect(
            translate("farm", lang),
            farms,
            farms)  # Todos los workspaces están seleccionados por defecto
    else:
        selector_farms = container.multiselect(
            translate("farm", lang),
            farms,
            placeholder=translate("choose_option", lang)) 

    ############################################################################
    # Capas
    ############################################################################

    # Filtra el DataFrame basado en las áreas seleccionadas
    filtered_df = filtered_df[filtered_df['farm_name'].isin(selector_farms)]

    # No obtengas los nombres únicos, en su lugar, utiliza todos los nombres
    capas = filtered_df['field_name'].tolist()

    # Diccionario para llevar un registro de los nombres de las capas y sus conteos
    capas_count = {}

    # Lista para almacenar los nombres de las capas modificados
    capas_modificadas = []

    for i, capa in enumerate(capas):
        if capa in capas_count:
            capas_count[capa] += 1
            nuevo_nombre = f"{capa} ({capas_count[capa]})"
            capas_modificadas.append(nuevo_nombre)
            filtered_df.loc[filtered_df.index[i], 'Nombre'] = nuevo_nombre
        else:
            capas_count[capa] = 1
            capas_modificadas.append(capa)

    container = st.container()
    select_all_capas = st.toggle(translate("select_all", lang), key='select_all_capas')

    if select_all_capas:
        selector_capas = container.multiselect(
            translate("yield_layers", lang),
            capas_modificadas,
            capas_modificadas)  # Todos los workspaces están seleccionados por defecto
    else:
        selector_capas = container.multiselect(
            translate("yield_layers", lang),
            capas_modificadas,
            placeholder=translate("choose_option", lang))

    ############################################################################
    # Powered by GeoAgro Picture
    ############################################################################

    st.markdown(
        """
        <style>
            div [data-testid=stImage]{
                bottom:0;
                display: flex;
                margin-bottom:10px;
            }
        </style>
        """, unsafe_allow_html=True
        )
        
    
    cI1,cI2,cI3=st.columns([1,4,1], gap="small")
    with cI1:
        pass
    with cI2:
        image = Image.open('assets/Powered by GeoAgro-01.png')
        new_image = image.resize((220, 35))
        st.image(new_image)
    with cI3:
        pass

############################################################################

if selector_capas:

    ############################################################################
    # Gráfico
    ############################################################################

    campos_agrupamiento = {
        translate("area", lang): 'area_name',
        translate("ws_field", lang): 'workspace_name',
        translate("season", lang): 'season_name',
        translate("farm_field", lang):'farm_name',
        translate("crop_field", lang): 'crop',
        translate("hybrid_variety_field", lang): 'hybrid'
    }

    st.markdown('')

    # Obtener el índice de 'Farm' en la lista de claves
    default_index = list(campos_agrupamiento.keys()).index(translate("farm_field", lang))
    # Selector para elegir una clave del diccionario
    selected_key = st.selectbox(translate('select_grouping_field', lang), options=list(campos_agrupamiento.keys()), index=default_index)
    # Obtén el valor asociado a la clave seleccionada
    selected_value = campos_agrupamiento[selected_key]
    # Ordenar el DataFrame primero por farm_name y luego por Rendimiento medio ajustado
    filtered_df = filtered_df.sort_values(by='Rendimiento final', ascending=False)

    st.markdown('')
    st.markdown(f"<b>{translate('adjusted_average_yield_by', lang)} {selected_key}</b>", unsafe_allow_html=True)

    # Crear un gráfico de barras interactivo con Plotly
    fig = px.bar(
        filtered_df,
        x='Nombre',
        y='Rendimiento final',
        color=selected_value,
        # title='Rendimiento medio ajustado por ' + selected_key,
        labels={translate("adjusted_average_yield", lang): translate("adjusted_average_yield", lang)},
        height=500,
        color_discrete_sequence=selected_colors  # Aquí se actualiza la paleta de colores
    )

    # Crear el hovertemplate personalizado
    hovertemplate = (
        f"<b>%{{x}}</b><br>"
        f"{translate('area', lang)}: %{{customdata[0]}}<br>"
        f"{translate('workspace', lang)}: %{{customdata[1]}}<br>"
        f"{translate('season', lang)}: %{{customdata[2]}}<br>"
        f"{translate('farm', lang)}: %{{customdata[3]}}<br>"
        f"{translate('field', lang)}: %{{customdata[4]}}<br>"
        f"{translate('crop', lang)}: %{{customdata[5]}}<br>"
        f"{translate('hybrid_variety', lang)}: %{{customdata[6]}}<br>"
        f"{translate('adjusted_average_yield', lang)}: %{{y:.2f}}"
    )

    # Obtener datos personalizados para el hovertemplate
    custom_data = filtered_df[['area_name', 'workspace_name', 'season_name', 'farm_name', 'field_name', 'crop', 'hybrid']].values

    # Aplicar el hovertemplate y datos personalizados al gráfico
    fig.update_traces(hovertemplate=hovertemplate, customdata=custom_data)

    # Personalizar la fuente del hoverlabel
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white", # color de fondo del hoverlabel
            font_size=12, # tamaño de la fuente
            font_family="Roboto" # tipo de fuente
        )
    )

    # Personalizar el tipo de fuente del gráfico
    fig.update_layout(
        font=dict(
            family="Roboto",  # Cambia 'Arial' a cualquier tipo de fuente que desees usar
            size=18,  # Cambia el tamaño de la fuente
        )
    )
    

    # Calcular el rendimiento promedio
    average_yield = round(filtered_df['Rendimiento final'].mean(), 2)

    # Agregar una línea de rendimiento promedio al gráfico
    line = go.Scatter(
        x=filtered_df['Nombre'].unique(),
        y=[average_yield] * len(filtered_df['Nombre'].unique()),
        mode='lines',
        name=translate('average_yield', lang),
        line=dict(color='black', dash='solid'),  # Puedes personalizar el color y el estilo de la línea aquí
        hovertemplate='%{y:.2f}',  # Configuración personalizada del hover
        hoverinfo='y'  # Muestra solo el valor de y en el hover
    )


    # Agregar la traza de la línea al gráfico
    fig.add_trace(line)

    # Personalizar el diseño del gráfico
    fig.update_xaxes(title_text=translate("yield_layer", lang))
    fig.update_yaxes(title_text=translate("adjusted_average_yield", lang))
    fig.update_layout(xaxis_tickangle=-45)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    ############################################################################
    # Gráfico 2
    ############################################################################

    st.markdown('')
    st.markdown(f"<b>{translate('weighted_yield_by', lang)} {selected_key}</b>", unsafe_allow_html=True)

    # Obtener los nombres de los grupos en el orden del 'Rendimiento medio ajustado'
    ordered_groups = filtered_df.sort_values(
        by='Rendimiento final', ascending=False
    )[selected_value].unique()

    # Agrupa por el valor seleccionado y calcula el rendimiento ponderado para cada grupo
    grouped = filtered_df.groupby(selected_value).apply(
        lambda x: x['Producción total'].sum() / x['hectares'].sum()
    ).reset_index()

    # Cambia el nombre de la columna 0 a 'Rendimiento Ponderado'
    grouped = grouped.rename(columns={0: 'Rendimiento Ponderado'})

    # Ordena el DataFrame 'grouped' según el orden de 'ordered_groups'
    grouped['order'] = grouped[selected_value].apply(lambda x: list(ordered_groups).index(x))
    grouped = grouped.sort_values('order').drop(columns='order')

    # Crear un gráfico de barras con Plotly
    fig = px.bar(
        grouped,
        x=selected_value,
        y='Rendimiento Ponderado',
        color=selected_value,
        # title=f'Rendimiento Ponderado por {selected_key}',
        # labels={'Rendimiento Ponderado': 'Rendimiento Ponderado'},
        height=500,
        color_discrete_sequence=selected_colors  # Aquí se actualiza la paleta de colores
    )

    hovertemplate = (
        translate('weighted_yield', lang) + ": %{y:.2f}"
    )

    # Obtener datos personalizados para el hovertemplate
    custom_data = grouped[['Rendimiento Ponderado']].values

    # Aplicar el hovertemplate y datos personalizados al gráfico
    fig.update_traces(hovertemplate=hovertemplate, customdata=custom_data)

    # Personalizar el diseño del gráfico
    fig.update_xaxes(title_text=selected_key)
    fig.update_yaxes(title_text=translate('weighted_yield', lang))
    fig.update_layout(xaxis_tickangle=-45)

    # Agregar anotaciones para mostrar los valores de Y sobre cada barra
    for i, val in enumerate(grouped['Rendimiento Ponderado']):
        fig.add_annotation(
            dict(
                x=grouped[selected_value].iloc[i], # posición x (nombre del grupo)
                y=val,  # posición y (valor de la barra)
                text=f'{val:.2f}',  # texto a mostrar (valor de la barra formateado)
                showarrow=False,  # no mostrar flecha
                yshift=10,  # ajustar la posición verticalmente para que no se superponga con la barra
                font=dict(size=15)  # tamaño de la fuente, color de la fuente, es opcional
            )
        )

    # Personalizar la fuente del hoverlabel
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white", # color de fondo del hoverlabel
            font_size=12, # tamaño de la fuente
            font_family="Roboto" # tipo de fuente
        )
    )

    # Personalizar el tipo de fuente del gráfico
    fig.update_layout(
        font=dict(
            family="Roboto",  # Cambia 'Arial' a cualquier tipo de fuente que desees usar
            size=18,  # Cambia el tamaño de la fuente
        )
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    ############################################################################
    # mapa
    ############################################################################

    # Mapear los colores del gráfico a los valores únicos de la columna de agrupamiento
    colors = selected_colors
    unique_values = filtered_df[selected_value].unique()
    color_map = {val: colors[i % len(colors)] for i, val in enumerate(unique_values)}
    filtered_df['color'] = filtered_df[selected_value].map(color_map)

    # Convertir la columna 'centroid' a objetos de geometría
    filtered_df['geometry'] = filtered_df['centroid'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(filtered_df, geometry='geometry')

    st.markdown('')
    st.markdown(f"<b>{translate('point_map_by_layer_according_to', lang)} {selected_key}</b>", unsafe_allow_html=True)

    # Crear mapa
    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=7)
    feature_groups = {}

    # Preparar los datos para el heatmap (una lista de listas, cada sublista contiene latitud, longitud y un valor para el heatmap)
    heat_data = [[row.geometry.y, row.geometry.x, row['Rendimiento final']] for idx, row in gdf.iterrows()] 

    for idx, row in gdf.iterrows():
        group_name = row[selected_value]
        if group_name not in feature_groups:
            feature_groups[group_name] = FeatureGroup(name=str(group_name))

        marker = folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=9,
            color=row['color'],
            fill=True,
            fill_opacity=0.8,
            fill_color=row['color'],
            tooltip=(
                "<span style='font-family:Roboto;'>"
                f"<b>{row['Nombre']}</b><br>"
                f"{translate('area', lang)}: {row['area_name']}<br>"
                f"{translate('workspace', lang)}: {row['workspace_name']}<br>"
                f"{translate('season', lang)}: {row['season_name']}<br>"
                f"{translate('farm', lang)}: {row['farm_name']}<br>"
                f"{translate('field', lang)}: {row['field_name']}<br>"
                f"{translate('crop', lang)}: {row['crop']}<br>"
                f"{translate('hybrid_variety', lang)}: {row['hybrid']}<br>"
                f"{translate('adjusted_average_yield', lang)}: {row['Rendimiento final']:.2f}"
                "</span>")
            )
        
        marker.add_to(feature_groups[group_name])

    for group_name, feature_group in feature_groups.items():
        feature_group.add_to(m)

    # Agregar heatmap al mapa como un layer adicional

    heatmap_feature_group = FeatureGroup(name=translate('heatmap', lang), show=False)  # Creamos un nuevo FeatureGroup para el heatmap
    HeatMap(heat_data).add_to(heatmap_feature_group)  # Agregamos el heatmap a este FeatureGroup
    heatmap_feature_group.add_to(m)  # Agregamos el FeatureGroup al mapa

    # Agrega la capa de teselas de Esri World Imagery
    tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}' 
    attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'

    # Agrega las capas de teselas adicionales y el control de capas
    folium.TileLayer(tiles, attr=attr, name='Esri World Imagery', show=True).add_to(m)

    LayerControl(collapsed=True).add_to(m)

    # m.save("map.html")

    folium_static(m, width=850)

    ############################################################################
    # descarga de csv
    ############################################################################
    # Convertir DataFrame a CSV
    # csv = filtered_df.to_csv(index=False)

    st.download_button(
        label=translate('download_csv', lang),
        data=marca_blanca,
        file_name=translate('title', lang) + ".csv",
        mime='text/csv',
    )


############################################################################
# advertencia
############################################################################

else:
    # Diccionario de referencia
    messages = {
        "select_yield_layer_warning": {
            "es": "Debe seleccionar una capa de rindes para continuar",
            "en": "You must select a yield layer to continue",
            "pt": "Você deve selecionar uma camada de rendimento para continuar"
        }
    }

    # Usar el valor de 'lang' para determinar el mensaje de advertencia
    if lang in messages["select_yield_layer_warning"]:
        advertencia = messages["select_yield_layer_warning"][lang]
        st.warning(advertencia)

st.caption("Powered by GeoAgro")
