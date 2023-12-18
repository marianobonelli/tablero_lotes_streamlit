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
    page_title="Tablero de Lotes y Cultivos",
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
    # Cultivos
    ############################################################################

    # Filtra el DataFrame basado en las áreas seleccionadas
    filtered_df = filtered_df[filtered_df['farm_name'].isin(selector_farms)]

    # No obtengas los nombres únicos, en su lugar, utiliza todos los nombres
    cultivos = sorted(filtered_df['crop'].unique().tolist())

    container = st.container()
    select_all_cultivos = st.toggle(translate("select_all", lang), value=True, key='select_all_cultivos')

    if select_all_cultivos:
        selector_cultivos = container.multiselect(
            translate("crop", lang),
            cultivos,
            cultivos)  # Todos los cultivos están seleccionados por defecto
    else:
        selector_cultivos = container.multiselect(
            translate("crop", lang),
            cultivos,
            placeholder=translate("choose_option", lang))
        
    ############################################################################
    # Híbridos / Variedades
    ############################################################################

    # Filtra el DataFrame basado en las áreas seleccionadas
    filtered_df = filtered_df[filtered_df['crop'].isin(selector_cultivos)]

    # No obtengas los nombres únicos, en su lugar, utiliza todos los nombres
    hibrido = sorted(filtered_df['hybrid'].unique().tolist())

    container = st.container()
    select_all_hibrido = st.toggle(translate("select_all", lang), value=True, key='select_all_hibrido')

    if select_all_hibrido:
        selector_hibrido = container.multiselect(
            translate("hybrid_variety", lang),
            hibrido,
            hibrido)  # Todos los hibrido están seleccionados por defecto
    else:
        selector_hibrido = container.multiselect(
            translate("hybrid_variety", lang),
            hibrido,
            placeholder=translate("choose_option", lang))
        
    # Filtra el DataFrame basado en las áreas seleccionadas
    filtered_df = filtered_df[filtered_df['hybrid'].isin(selector_hibrido)]

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

if selector_hibrido:

    st.markdown('')

    ############################################################################
    # Metricas
    ############################################################################

    col1, col2, col3, col4, col5 = st.columns(5)

    # Establecimientos
    col1.metric(
        translate("farms", lang), 
        len(filtered_df['farm_name'].unique())
    )

    # Lotes
    total_lotes = len(filtered_df['field_name'])
    col2.metric(
        translate("fields", lang), 
        total_lotes
    )

    # Hectáreas
    total_hectareas = sum(filtered_df['hectares'])  # Suma sin convertir a miles
    col3.metric(
        translate("hectares", lang), 
        f"{total_hectareas:,.0f}"  # Formatea con separadores de miles y sin decimales
    )

    # Cultivos
    col4.metric(
        translate("crops", lang), 
        len(filtered_df['crop'].unique())
    )

    # Híbridos
    col5.metric(
        translate("hybrid_varieties", lang), 
        len(filtered_df['hybrid'].unique())
    )
        
    ############################################################################

    # Agregar las métricas
    col1, col2, col3, col4, col5 = st.columns(5)

    # Lotes sin cultivo
    lotes_sin_cultivo = len(filtered_df[filtered_df['crop'] == '-No asignado-'])
    porcentaje_sin_cultivo = (lotes_sin_cultivo / total_lotes) * -100 if total_lotes > 0 else 0

    col1.metric(
        translate("fields_without_crops", lang), 
        lotes_sin_cultivo, 
        f"{porcentaje_sin_cultivo:.2f}%"
    )

    # Lotes sin híbrido
    lotes_sin_hibrido = len(filtered_df[filtered_df['hybrid'] == '-No asignado-'])
    porcentaje_sin_hibrido = (lotes_sin_hibrido / total_lotes) * -100 if total_lotes > 0 else 0

    col2.metric(
        translate("fields_without_hybrids_or_varieties", lang), 
        lotes_sin_hibrido, 
        f"{porcentaje_sin_hibrido:.2f}%"
    )

    # Lotes sin fecha de siembra
    lotes_sin_fecha_siembra = len(filtered_df[pd.isna(filtered_df['crop_date'])])
    porcentaje_sin_fecha_siembra = (lotes_sin_fecha_siembra / total_lotes) * -100 if total_lotes > 0 else 0

    col3.metric(
        translate("fields_without_sowing_date", lang), 
        lotes_sin_fecha_siembra, 
        f"{porcentaje_sin_fecha_siembra:.2f}%"
    )

    ############################################################################
    # Agrupar valores por
    ############################################################################

    campos_agrupamiento = {
        translate("area", lang): 'area_name',
        translate("ws_field", lang): 'workspace_name',
        translate("season", lang): 'season_name',
        translate("farm_field", lang):'farm_name',
        translate("crop_field", lang): 'crop',
        translate("hybrid_variety", lang): 'hybrid'
    }

    st.markdown('')

    # Obtener el índice de 'Farm' en la lista de claves
    default_index = list(campos_agrupamiento.keys()).index(translate("crop_field", lang))
    # Selector para elegir una clave del diccionario
    selected_key = st.selectbox(translate('select_grouping_field', lang), options=list(campos_agrupamiento.keys()), index=default_index)
    # Obtén el valor asociado a la clave seleccionada
    selected_value = campos_agrupamiento[selected_key]
    # Ordenar el DataFrame primero por farm_name y luego por Rendimiento medio ajustado
    filtered_df = filtered_df.sort_values(by='hectares', ascending=False)

    # Agrupar el DataFrame por el valor seleccionado y sumar las hectáreas
    grouped_df = filtered_df.groupby(selected_value)['hectares'].sum().reset_index()

    # Ordenar el DataFrame agrupado por hectáreas en orden descendente
    grouped_df = grouped_df.sort_values(by='hectares', ascending=False)

    ############################################################################
    # Gráfico de torta
    ############################################################################

    st.markdown('')
    st.markdown(f"<b>{translate('hectares_by', lang)} {selected_key}</b>", unsafe_allow_html=True)

    # Crear un gráfico de torta con Plotly Express
    pie_fig = px.pie(
        grouped_df,
        names=selected_value,  # Usa el valor seleccionado como etiquetas
        values='hectares',     # Usa las hectáreas como valores
        color=selected_value,  # Colorea según el valor seleccionado
        color_discrete_sequence=selected_colors  # Utiliza la misma paleta de colores
    )

    # Crear el hovertemplate personalizado
    hovertemplate = (
        f"<b>%{{label}}</b><br>"
        f"{translate('hectares', lang)}: %{{value}}<br>"
        f"Porcentaje: %{{percent:.2%}}"  # Multiplica por 100 y muestra como porcentaje
    )

    # Personalizar el gráfico de torta para que el texto quede por fuera
    pie_fig.update_traces(
        textinfo='percent+label',
        textposition='outside',
        outsidetextfont=dict(family="Roboto", size=12),
        pull=0.02,
        texttemplate='%{label} %{percent:.2%}',  # Multiplica por 100 para mostrar el porcentaje correctamente
        hovertemplate=hovertemplate
    )

    pie_fig.update_layout(
        font=dict(family="Roboto", size=18)
        )

    # Mostrar el gráfico de torta en Streamlit
    st.plotly_chart(pie_fig, use_container_width=True)

    ############################################################################
    # Gráfico de barras
    ############################################################################

    st.markdown('')
    st.markdown(f"<b>{translate('hectares_by', lang)} {selected_key}</b>", unsafe_allow_html=True)

    # Crear un gráfico de barras interactivo con Plotly
    fig = px.bar(
        grouped_df,
        x=selected_value,  # Usa el valor seleccionado como eje X
        y='hectares',      # Hectáreas como eje Y
        color=selected_value,
        labels={selected_value: selected_key, 'hectares': translate('hectares', lang)},
        height=500,
        color_discrete_sequence=selected_colors  # Aquí se actualiza la paleta de colores
    )

    # Crear el hovertemplate personalizado
    hovertemplate = (
        f"<b>%{{x}}</b><br>"
        f"{translate('hectares', lang)}: %{{y:.2f}}<br>"
    )

    # Aplicar el hovertemplate y datos personalizados al gráfico
    fig.update_traces(hovertemplate=hovertemplate)

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
    
    # Personalizar el diseño del gráfico
    fig.update_xaxes(title_text=selected_key)
    fig.update_yaxes(title_text=translate("hectares", lang))
    fig.update_layout(xaxis_tickangle=-45)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    ############################################################################
    # mapa
    ############################################################################

    # Calcular la suma total de hectáreas para cada valor de 'selected_value' y crear un campo de orden
    hectares_order = filtered_df.groupby(selected_value)['hectares'].sum().sort_values(ascending=False).reset_index()
    hectares_order['order'] = range(1, len(hectares_order) + 1)

    # Unir esta información con el DataFrame original para añadir el campo de orden
    filtered_df = pd.merge(filtered_df, hectares_order[[selected_value, 'order']], on=selected_value, how='left')

    # Mapear los colores del gráfico a los valores únicos de la columna de orden
    colors = selected_colors
    color_map = {val: colors[i % len(colors)] for i, val in enumerate(hectares_order['order'])}
    filtered_df['color'] = filtered_df['order'].map(color_map)

    # Convertir la columna 'centroid' a objetos de geometría
    filtered_df['geometry'] = filtered_df['centroid'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(filtered_df, geometry='geometry')

    st.markdown('')
    st.markdown(f"<b>{translate('point_map_by_field_according_to', lang)} {selected_key}</b>", unsafe_allow_html=True)

    # Crear mapa
    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=7)
    feature_groups = {}

    # Preparar los datos para el heatmap
    heat_data = [[row.geometry.y, row.geometry.x, row['hectares']] for idx, row in gdf.iterrows()]

    for group_name in grouped_df[selected_value]:
        for idx, row in filtered_df[filtered_df[selected_value] == group_name].iterrows():
            group_name = row[selected_value]
            if group_name not in feature_groups:
                feature_groups[group_name] = FeatureGroup(name=str(group_name))

            marker = folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=7,
                color=row['color'],
                fill=True,
                fill_opacity=0.8,
                fill_color=row['color'],
                tooltip=(
                    "<span style='font-family:Roboto;'>"
                    f"{translate('area', lang)}: {row['area_name']}<br>"
                    f"{translate('workspace', lang)}: {row['workspace_name']}<br>"
                    f"{translate('season', lang)}: {row['season_name']}<br>"
                    f"{translate('farm', lang)}: {row['farm_name']}<br>"
                    f"{translate('field', lang)}: {row['field_name']}<br>"
                    f"{translate('crop', lang)}: {row['crop']}<br>"
                    f"{translate('hybrid_variety', lang)}: {row['hybrid']}<br>"
                    f"{translate('seeding_date', lang)}: {row['crop_date']}<br>"
                    f"{translate('hectares', lang)}: {row['hectares']}<br>"
                    "</span>")
            )
            marker.add_to(feature_groups[group_name])

    for group_name, feature_group in feature_groups.items():
        feature_group.add_to(m)

    # Agregar heatmap al mapa como un layer adicional
    heatmap_feature_group = FeatureGroup(name=translate('heatmap', lang), show=False)
    HeatMap(heat_data).add_to(heatmap_feature_group)
    heatmap_feature_group.add_to(m)

    # Agrega la capa de teselas de Esri World Imagery
    tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    folium.TileLayer(tiles, attr=attr, name='Esri World Imagery', show=True).add_to(m)

    LayerControl(collapsed=True).add_to(m)

    # m.save("map.html")
    folium_static(m, width=900)

    ############################################################################
    # timeline
    ############################################################################

    st.markdown('')
    st.markdown(f"<b>{translate('seeding_date_by', lang)} {selected_key}</b>", unsafe_allow_html=True)

    # Convertir la fecha de siembra a tipo datetime y crear columnas de inicio y fin
    filtered_df['crop_date'] = pd.to_datetime(filtered_df['crop_date'])
    filtered_df['start_date'] = filtered_df['crop_date']
    filtered_df['end_date'] = filtered_df['crop_date'] + pd.Timedelta(days=1)

    # Ordenar el DataFrame por el campo de orden antes de crear el gráfico de Gantt
    filtered_df = filtered_df.sort_values(by='order')

    # Agrupar por 'selected_value' y fecha, concatenando los nombres de lotes y establecimientos
    grouped = filtered_df.groupby([selected_value, 'crop_date']).apply(
        lambda x: ' | '.join(x['field_name'] + ' - ' + x['farm_name'])
    ).reset_index(name='info')

    # Combinar la información agrupada con el DataFrame original
    filtered_df = pd.merge(filtered_df, grouped, on=[selected_value, 'crop_date'])

    # Crear el gráfico de Gantt
    fig = px.timeline(
        filtered_df,
        x_start='start_date',
        x_end='end_date',
        y=selected_value,
        color=selected_value,
        labels={'crop_date': translate('seeding_date', lang), selected_value: selected_key},
        height=600,
        color_discrete_sequence=selected_colors
    )

    # Añadir líneas verticales para cada cambio de año
    years = filtered_df['crop_date'].dt.year.unique()
    for year in years:
        fig.add_vline(x=pd.to_datetime(f'{year}-12-31'), line_width=0.5, line_dash="solid", line_color="grey")
        for month in [2,3,4,5,6,7,8,9,10,11,12]:
            fig.add_vline(x=pd.to_datetime(f'{year}-{month}-01'), line_width=0.05, line_dash="solid", line_color="grey")

    # Configurar el formato y diseño del gráfico
    fig.update_layout(
        font=dict(family="Roboto", size=16),
        xaxis_title=translate('seeding_date', lang),
        yaxis_title=selected_key,
        xaxis=dict(type='date'),
        yaxis=dict(showgrid=True)
    )

    # Configurar el hovertemplate para mostrar la información de lotes y establecimientos
    fig.update_traces(hovertemplate="%{y}<br>%{x}<br><br>%{customdata[0]}")
    fig.update_traces(customdata=filtered_df[['info']])

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)


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
        "select_warning": {
            "es": "Debe seleccionar un cultivo para continuar",
            "en": "You must select a crop to continue",
            "pt": "Você deve selecionar um cultivo para continuar"
        }
    }

    # Usar el valor de 'lang' para determinar el mensaje de advertencia
    if lang in messages["select_warning"]:
        advertencia = messages["select_warning"][lang]
        st.warning(advertencia)

st.caption("Powered by GeoAgro")
