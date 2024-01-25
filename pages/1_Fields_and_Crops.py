# Importar bibliotecas para manipulación de datos
import pandas as pd
import geopandas as gpd
from shapely import wkt

# Importar bibliotecas para visualización
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import folium
from folium import FeatureGroup, LayerControl
from folium.plugins import HeatMap

# Importar bibliotecas para integración web y Streamlit
import streamlit as st
from streamlit_folium import st_folium
from streamlit_extras.metric_cards import style_metric_cards 
from streamlit_vertical_slider import vertical_slider 

# Importar bibliotecas para manejo de imágenes
from PIL import Image

# Importar módulos o paquetes locales
from helper import translate

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
    menu_items={
        'Get Help': 'https://geoagro1.atlassian.net/servicedesk/customer/portal/5',
        'Report a bug': "https://geoagro1.atlassian.net/servicedesk/customer/portal/5",
        'About': "Dashboards. Powered by GeoAgro"
    }
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#####################   API   #####################

# Read the CSV file into a DataFrame
# filtered_df = pd.read_csv('csv_rindes.csv')
user_info = {'email': "mbonelli@geoagro.com", 'language': 'es', 'env': 'prod', 'domainId': 1, 'areaId': None, 'workspaceId': None, 'seasonId': None, 'farmId': None}
marca_blanca = 'assets/GeoAgro_principal.png'

#####################
import requests

# Función para realizar la llamada a la API y cachear la respuesta
@st.cache_data
def api_call():
    response = requests.post(url, json={'query': query}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

access_key_id = st.secrets["API_key"]

# URL de tu API GraphQL y headers
url = 'https://lpul7iylefbdlepxbtbovin4zy.appsync-api.us-west-2.amazonaws.com/graphql'
headers = {
    'x-api-key': access_key_id,
    'Content-Type': 'application/json'
}

# Tu consulta GraphQL
query = f'''
query MyQuery {{
  get_field_table(domainId: {user_info['domainId']}, email: "{user_info['email']}", exportAllAsCsv: true, lang: "{user_info['language']}", withHectares: true, withCentroid: true, withGeom: true, delimiter: ";") {{
    csvUrl
  }}
}}
'''

# Llamar a la función api_call que está cacheada
data = api_call()

@st.cache_data  # 👈 Add the caching decorator
def load_data(url):
    df = pd.read_csv(url, delimiter=";")
    return df

# Verificar y manejar la respuesta
if data:
    csv_url = data['data']['get_field_table']['csvUrl']
    filtered_df = load_data(csv_url)
    # Procesar filtered_df
else:
    st.error("No se pudo obtener datos de la API.")

##################### USER INFO #####################

language = user_info['language']
email = user_info['email']
env = user_info['env']
st.session_state['env'] = env

##################### LANGUAGE  #####################

c_1, c_2, c_3 = st.columns([1.5, 4.5, 1], gap="small")

with c_1:
    image_mb = Image.open(marca_blanca)
    # image_mb = image_mb.resize((220, 35))
    st.image(image_mb)

# with c_3:   
#     try:
#         langs = ['es', 'en', 'pt']
#         if language is not None:
#             lang = st.selectbox(translate("language", language), label_visibility="hidden", options=langs, index=langs.index(language))
#         else:  # from public link
#             lang = st.selectbox(translate("es", language), label_visibility="hidden", options=langs)
        
#         st.session_state['lang'] = lang
#     except Exception as exception:
#         lang = "es"
#         st.session_state['lang'] = lang
#         pass

# lang = st.session_state['lang']

try:
    lang = st.session_state['lang']
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
    st.markdown('')
    st.markdown('')


    # Obtener la lista de rampas de colores cualitativos
    # color_ramps = dir(px.colors.qualitative)
    # Filtrar los elementos que no son rampas de colores
    # color_ramps = [ramp for ramp in color_ramps if not ramp.startswith("__")]
    # Encontrar el índice de 'T10' en la lista de rampas de colores
    # default_index = color_ramps.index('T10') if 'T10' in color_ramps else 0

    # Selector para la rampa de colores con un valor predeterminado
    # selected_color_ramp = st.selectbox(translate("color_palette", lang), color_ramps, index=default_index)

    # Usa getattr para obtener la rampa de colores seleccionada
    # selected_colors = getattr(px.colors.qualitative, selected_color_ramp)

    selected_colors = px.colors.qualitative.T10

    ############################################################################
    # Area
    ############################################################################

    # Reemplaza valores en blanco o nulos en 'area_name' por '--'
    filtered_df['area_name'].fillna('--', inplace=True)

    # Luego continúa con el proceso como antes
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

    st.divider()  # 👈 Draws a horizontal rule
    st.markdown('')
    st.markdown(f"<b>{translate('metrics', lang)}</b>", unsafe_allow_html=True)

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
    # Redondear a cero si es muy cercano a cero
    if abs(porcentaje_sin_cultivo) < 0.001:
        porcentaje_sin_cultivo = 0

    col1.metric(
        translate("fields_without_crops", lang), 
        lotes_sin_cultivo, 
        f"{porcentaje_sin_cultivo:.2f}%",
        # delta_color = "off" if porcentaje_sin_cultivo == 0 else "normal"
        
    )

    # Lotes sin híbrido
    lotes_sin_hibrido = len(filtered_df[filtered_df['hybrid'] == '-No asignado-'])
    porcentaje_sin_hibrido = (lotes_sin_hibrido / total_lotes) * -100 if total_lotes > 0 else 0
    # Redondear a cero si es muy cercano a cero
    if abs(porcentaje_sin_hibrido) < 0.001:
        porcentaje_sin_hibrido = 0

    col2.metric(
        translate("fields_without_hybrids_or_varieties", lang), 
        lotes_sin_hibrido, 
        f"{porcentaje_sin_hibrido:.2f}%",
        # delta_color = "off" if porcentaje_sin_hibrido == 0 else "normal"
    )

    # Lotes sin fecha de siembra
    lotes_sin_fecha_siembra = len(filtered_df[pd.isna(filtered_df['crop_date'])])
    porcentaje_sin_fecha_siembra = (lotes_sin_fecha_siembra / total_lotes) * -100 if total_lotes > 0 else 0
    # Redondear a cero si es muy cercano a cero
    if abs(porcentaje_sin_fecha_siembra) < 0.001:
        porcentaje_sin_fecha_siembra = 0

    col3.metric(
        translate("fields_without_sowing_date", lang), 
        lotes_sin_fecha_siembra, 
        f"{porcentaje_sin_fecha_siembra:.2f}%",
        # delta_color = "off" if porcentaje_sin_fecha_siembra == 0 else "normal"
    )

    style_metric_cards(border_left_color="#0e112c", box_shadow=False)

    ############################################################################
    # Agrupar valores por
    ############################################################################

    campos_agrupamiento = {
        translate("area", lang): 'area_name',
        translate("workspace", lang): 'workspace_name',
        translate("season", lang): 'season_name',
        translate("farm", lang):'farm_name',
        translate("crop", lang): 'crop',
        translate("hybrid_variety", lang): 'hybrid'
    }

    st.divider()  # Draws a horizontal rule
    st.markdown('')

    # Obtener el índice de 'Farm' en la lista de claves
    default_index = list(campos_agrupamiento.keys()).index(translate("crop", lang))
    # Selector para elegir una clave del diccionario
    selected_key = st.selectbox(translate('select_grouping_field', lang), options=list(campos_agrupamiento.keys()), index=default_index)
    # Obtén el valor asociado a la clave seleccionada
    selected_value = campos_agrupamiento[selected_key]
    # Ordenar el DataFrame primero por farm_name y luego por Rendimiento medio ajustado
    filtered_df = filtered_df.sort_values(by='hectares', ascending=False)

    ####
    from streamlit_extras.mandatory_date_range import date_range_picker

    # Asegúrate de que 'crop_date' está en formato datetime
    filtered_df['crop_date'] = pd.to_datetime(filtered_df['crop_date'], errors='coerce')

    # Organizar los widgets en dos columnas
    col1, col2 = st.columns([2, 1])

    # Opción para incluir/excluir/solo sin fecha asignada
    date_option = col2.selectbox(translate("fields_without_sowing_date", lang), 
                                [translate("include", lang), translate("exclude", lang), translate("only_no_date", lang)])

    # Determinar el rango de fechas disponible
    min_date = filtered_df['crop_date'].min()
    max_date = filtered_df['crop_date'].max()

    # Desactivar el selector de fechas si se selecciona 'Solo Sin Fecha'
    date_input_disabled = date_option == translate("only_no_date", lang)

    with col1:
        # Si hay fechas válidas, muestra el selector de rango de fechas
        if pd.notnull(min_date) and pd.notnull(max_date) and not date_input_disabled:
            selected_date_range = date_range_picker(translate("select_date_range", lang),
                                                    default_start=min_date.date() if min_date else None,
                                                    default_end=max_date.date() if max_date else None, 
                                                    min_date=min_date.date() if min_date else None, 
                                                    max_date=max_date.date() if max_date else None,
                                                    error_message=translate("error_message_date_picker", lang) 
                                                    )
            start_date, end_date = [pd.Timestamp(date) for date in selected_date_range]
        elif date_input_disabled:
            start_date, end_date = min_date, max_date

    # Aplicar filtro basado en la selección de fecha y el rango de fechas seleccionado
    if date_option == translate("include", lang):
        df_original = filtered_df
        filtered_df = filtered_df[(filtered_df['crop_date'] >= start_date) & 
                                (filtered_df['crop_date'] <= end_date) | 
                                filtered_df['crop_date'].isna()]
    elif date_option == translate("exclude", lang):
        df_original = filtered_df
        filtered_df = filtered_df[(filtered_df['crop_date'] >= start_date) & 
                                (filtered_df['crop_date'] <= end_date)]
    elif date_option == translate("only_no_date", lang):
        filtered_df = filtered_df[filtered_df['crop_date'].isna()]

    #
        
    # Comprobar si filtered_df está vacío
    if filtered_df.empty:
        st.warning(translate("select_warning", lang))
    else:

        # Agrupar el DataFrame por el valor seleccionado y sumar las hectáreas
        grouped_df = filtered_df.groupby(selected_value)['hectares'].sum().reset_index()

        # Ordenar el DataFrame agrupado por hectáreas en orden descendente
        grouped_df = grouped_df.sort_values(by='hectares', ascending=False)

        ############################################################################
        # Gráfico de torta
        ############################################################################

        st.markdown('')
        st.markdown(f"<b>{translate('hectares_by', lang)} {selected_key}</b>", unsafe_allow_html=True)

        # Crear columnas para el control deslizante y el gráfico
        col1, col2 = st.columns([2,10])  # Cambio aquí: de 'ol1, col2' a 'col1, col2'

        # En la primera columna (col1), añadir el control deslizante
        with col1:
            st.markdown('')
            st.markdown('')
            st.markdown('')
            st.markdown('')
            st.markdown('')

            rotation = vertical_slider(
                key="Rotación del gráfico", 
                thumb_shape = "pill", #Optional - Defaults to "circle"
                default_value=0,
                step=5,
                min_value=0,
                max_value=360,
                track_color="lightgray",  # optional
                thumb_color="#0e112c",  # optional
                slider_color="lightgray",  # optional
                value_always_visible = False ,
            )

        # En la segunda columna (col2), mostrar el gráfico
        with col2:
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

            # Actualizar la rotación del gráfico
            pie_fig.update_traces(
                rotation=rotation  # Actualiza la rotación del gráfico de torta
            )

            # Mostrar el gráfico actualizado
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

        # # Markdown
        # st.markdown('')
        # st.markdown(f"<b>{translate('point_map_by_field_according_to', lang)} {selected_key}</b>", unsafe_allow_html=True)

        # Ordenar df
        # Calcular la suma total de hectáreas para cada valor de 'selected_value' y crear un campo de orden
        hectares_order = filtered_df.groupby(selected_value)['hectares'].sum().sort_values(ascending=False).reset_index()
        hectares_order['order'] = range(1, len(hectares_order) + 1)

        # Unir esta información con el DataFrame original para añadir el campo de orden
        filtered_df = pd.merge(filtered_df, hectares_order[[selected_value, 'order']], on=selected_value, how='left')

        # Mapear los colores del gráfico a los valores únicos de la columna de orden
        colors = selected_colors
        color_map = {val: colors[i % len(colors)] for i, val in enumerate(hectares_order['order'])}
        filtered_df['color'] = filtered_df['order'].map(color_map)

        # Añadir un identificador único a cada fila
        if 'id' not in filtered_df.columns:
            filtered_df['id'] = filtered_df.index

        # Crear un diccionario para mapear los identificadores a colores
        id_to_color = dict(zip(filtered_df['id'], filtered_df['color']))

        # Generador de los gdf:
        @st.cache_data  # 👈 Add the caching decorator
        def generate_gdf_polygons(df):
            df_poly = df.copy()
            df_poly['geometry'] = df_poly['geom'].apply(wkt.loads)
            gdf = gpd.GeoDataFrame(df_poly, geometry='geometry')
            return gdf
        
        # Crear un GeoDataFrame usando la columna de geometría convertida
        gdf_poly = generate_gdf_polygons(filtered_df)

        @st.cache_data
        def generate_gdf_points(df):
            df_point = df.copy()
            df_point = df_point.drop(columns='geom')
            df_point['geometry'] = df_point['centroid'].apply(wkt.loads)
            gdf = gpd.GeoDataFrame(df_point, geometry='geometry')
            return gdf
        
        # Crear un GeoDataFrame usando la columna de geometría convertida
        gdf_point = generate_gdf_points(filtered_df)

        # Organizar los widgets en dos columnas
        col1, col2 = st.columns([3,1])

        # Columna 1: Markdowns
        with col1:
            st.markdown('')
            st.markdown('')
            st.markdown(f"<b>{translate('point_map_by_field_according_to', lang)} {selected_key}</b>", unsafe_allow_html=True)

        # Columna 2: Selector de puntos o polígonos
        with col2:
            # Opción para incluir/excluir/solo sin fecha asignada
            tipo_de_mapa = col2.selectbox("", [translate("points", lang), translate("polygons", lang)])

        
        if tipo_de_mapa == translate("points", lang):
            # Crear mapa
            m = folium.Map(location=[gdf_point.geometry.centroid.y.mean(), gdf_point.geometry.centroid.x.mean()], zoom_start=7)
            feature_groups = {}

            # Preparar los datos para el heatmap
            heat_data = [[row.geometry.y, row.geometry.x, row['hectares']] for idx, row in gdf_point.iterrows()]

            for group_name in grouped_df[selected_value]:
                for idx, row in gdf_point[gdf_point[selected_value] == group_name].iterrows():
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
            heatmap_feature_group = FeatureGroup(name=translate('heatmap', lang), show=True)
            HeatMap(heat_data).add_to(heatmap_feature_group)
            heatmap_feature_group.add_to(m)

            # Agrega la capa de teselas de Esri World Imagery
            tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
            attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            folium.TileLayer(tiles, attr=attr, name='Esri World Imagery', show=True).add_to(m)

            LayerControl(collapsed=True).add_to(m)

            # m.save("map.html")
            st_folium(m, use_container_width=True)

        elif tipo_de_mapa == translate("polygons", lang):

            # Crear mapa
            m = folium.Map(location=[gdf_poly.geometry.centroid.y.mean(), gdf_poly.geometry.centroid.x.mean()], zoom_start=7)

            # Preparar los datos para los grupos de características, respetando el orden
            feature_groups = {name: FeatureGroup(name=str(name)) for name in hectares_order[selected_value]}

            for idx, row in gdf_poly.iterrows():
                # Aquí se puede personalizar el contenido del tooltip
                tooltip_content = (
                    f"<span style='font-family:Roboto;'>"
                    f"{translate('area', lang)}: {row['area_name']}<br>"
                    f"{translate('workspace', lang)}: {row['workspace_name']}<br>"
                    f"{translate('season', lang)}: {row['season_name']}<br>"
                    f"{translate('farm', lang)}: {row['farm_name']}<br>"
                    f"{translate('field', lang)}: {row['field_name']}<br>"
                    f"{translate('crop', lang)}: {row['crop']}<br>"
                    f"{translate('hybrid_variety', lang)}: {row['hybrid']}<br>"
                    f"{translate('seeding_date', lang)}: {row['crop_date']}<br>"
                    f"{translate('hectares', lang)}: {row['hectares']}<br>"
                    "</span>"
                )

                
                folium.GeoJson(
                    row.geometry,
                    style_function=lambda feature, id=row['id']: {
                        "fillColor": id_to_color[id],
                        "color": id_to_color[id],
                        "weight": 2,
                        "fillOpacity": 0.6
                    },
                    tooltip=tooltip_content
                ).add_to(feature_groups[row[selected_value]])

            # Agregar los grupos de características al mapa en el orden correcto
            for name in hectares_order[selected_value]:
                feature_groups[name].add_to(m)

            # Agrega la capa de teselas de Esri World Imagery y el control de capas
            tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
            attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            folium.TileLayer(tiles, attr=attr, name='Esri World Imagery', show=True).add_to(m)
            LayerControl(collapsed=True).add_to(m)

            # Mostrar el mapa en Streamlit
            st_folium(m, use_container_width=True)

        ############################################################################
        # timeline
        ############################################################################

        # Verificar si hay fechas de siembra válidas en el DataFrame filtrado
        if not filtered_df['crop_date'].isna().all():   

            st.markdown('')
            st.markdown(f"<b>{translate('seeding_date_by', lang)} {selected_key}</b>", unsafe_allow_html=True)

            tab1, tab2 = st.tabs([translate('seeding_date', lang), translate('hectares_per_date', lang)])

            with tab1:

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


                # Crear dos columnas, la primera de un cuarto y la segunda de tres cuartos
                col1, col2 = st.columns([4, 1])

                with col1:

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

                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:

                    # Asegurarte de que df_original esté agrupado por selected_value
                    df_original_filtered = df_original.groupby(selected_value)
                    # Calcular el total de hectáreas en df_original
                    total_hectares_original = df_original_filtered['hectares'].sum()

                    # Calcular el porcentaje de hectáreas sembradas para cada selected_value en filtered_df
                    percentage_df = filtered_df.groupby(selected_value)['hectares'].sum() / total_hectares_original * 100

                    # Eliminar valores con porcentaje igual a 0 y mantener el mismo orden que el gráfico de Gantt
                    percentage_df = percentage_df[percentage_df > 0].reindex(filtered_df[selected_value].unique())

                    # Crear un gráfico de barras horizontales para mostrar los porcentajes
                    fig_bar = px.bar(percentage_df.reset_index(), x='hectares', y=selected_value, orientation='h',
                                    color=selected_value, color_discrete_sequence=selected_colors)
                    
                    # Configurar el hovertemplate para mostrar la información deseada
                    fig_bar.update_traces(hovertemplate="%{y}<br>%{x:.2f}%<br>") 

                    # Añadir anotaciones de texto con los porcentajes
                    for index, row in percentage_df.reset_index().iterrows():
                        fig_bar.add_annotation(
                            x=row['hectares'],
                            y=row[selected_value],
                            text=f"{row['hectares']:.1f} %",  # Formato de dos decimales para el porcentaje
                            showarrow=False,
                            font=dict(color='black'),
                            xref="x",
                            yref="y",
                            xanchor="left",
                            yanchor="middle"
                        )

                    fig_bar.update_layout(
                        xaxis_title=translate('seeding_progress', lang) + ' %',
                        yaxis=dict(showticklabels=False, title=''),  # Eliminar las referencias del eje Y
                        showlegend=False,
                        height=600  # Ajustar la altura aquí
                    )
                    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

            with tab2:

                # Crear dos columnas, la primera ocupa dos tercios y la segunda un tercio
                col1, col2 = st.columns([3,1])

                with col1:     
                    st.markdown('')   
                    # Código existente para la selección y la creación del gráfico
                    selected_analysis_value = st.selectbox(selected_key, filtered_df[selected_value].unique())
                    # Filtrar el DataFrame basado en el valor seleccionado
                    analysis_df = filtered_df[filtered_df[selected_value] == selected_analysis_value]
                    df_original = df_original[df_original[selected_value] == selected_analysis_value]

                with col2:
                    # Calcular el porcentaje de hectáreas
                    selected_hectares = analysis_df['hectares'].sum()
                    total_hectares = df_original['hectares'].sum()
                    percentage = (selected_hectares / total_hectares) * 100

                    # Mostrar el métrico en la segunda columna
                    st.metric(
                        label = translate('seeding_progress', lang),
                        value = f"{selected_hectares:,.2f} ha",
                        delta = f"{percentage:.2f}%"
                        )

                # Agrupar los datos por fecha para el gráfico de barras
                bar_data = analysis_df.groupby('crop_date').agg({'hectares': 'sum'}).reset_index()

                # Agrupar los datos por fecha y calcular el total acumulado de hectáreas para el gráfico de línea
                line_data = analysis_df.groupby('crop_date').agg({'hectares': 'sum'}).cumsum().reset_index()

                # Crear un gráfico de figura con ejes secundarios
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # Agregar el gráfico de barras (hectáreas por fecha sin agrupar)
                fig.add_trace(
                    go.Bar(x=bar_data['crop_date'], y=bar_data['hectares'], name=translate('hectares_per_date', lang)),
                    secondary_y=False,
                )

                # Agregar el gráfico de línea (total acumulado de hectáreas)
                fig.add_trace(
                    go.Scatter(x=line_data['crop_date'], y=line_data['hectares'], name=translate('accumulated_hectares', lang), mode='lines+markers'),
                    secondary_y=True,
                )

                # Configurar títulos de ejes y diseño del gráfico
                fig.update_layout(
                    font=dict(family="Roboto", size=16),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.25,  # Ajusta este valor para bajar la leyenda y que no tape las referencias del eje X
                        xanchor="center",
                        x=0.5
                    )
                )

                fig.update_xaxes(title_text=translate('seeding_date', lang))
                
                # Actualizar ejes Y para no mostrar la cuadrícula
                fig.update_yaxes(
                    title_text=translate('hectares_per_date', lang),
                    # showgrid=False,
                    secondary_y=False)
                
                fig.update_yaxes(
                    title_text=translate('accumulated_hectares', lang),
                    showgrid=False,
                    secondary_y=True)

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
    st.warning(translate("select_warning", lang))

st.caption("Powered by GeoAgro")
