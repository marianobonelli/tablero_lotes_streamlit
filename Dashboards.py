# Importar bibliotecas para integración web y Streamlit
import streamlit as st
import requests  

# Importar bibliotecas para manejo de imágenes
from PIL import Image, UnidentifiedImageError
import base64
import io
import binascii

# Importar módulos o paquetes locales
from helper import translate, api_call_logo

############################################################################
# Estilo
############################################################################

# # Cargar la imagen
# page_icon = Image.open("assets/favicon geoagro nuevo-13.png")

st.set_page_config(
    page_title="Dashboards",
    page_icon=Image.open("assets/favicon geoagro nuevo-13.png"),
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

###################   User info   ##################

# Read the CSV file into a DataFrame
# filtered_df = pd.read_csv('csv_rindes.csv')
user_info = {'email': "mbonelli@geoagro.com", 'language': 'es', 'env': 'prod', 'domainId': 1, 'areaId': None, 'workspaceId': None, 'seasonId': None, 'farmId': None}

##################### API Logo Marca Blanca #####################

access_key_id = st.secrets["API_key"]
default_logo='assets/GeoAgro_principal.png'

@st.cache_data
def get_logo(user_info, access_key_id, default_logo_path):
    logo_image = api_call_logo(user_info, access_key_id, default_logo_path)
    return logo_image

logo_image = get_logo(user_info, access_key_id, default_logo_path='assets/GeoAgro_principal.png')
st.session_state['logo_image'] = logo_image

##################### USER INFO #####################

language = user_info['language']
email = user_info['email']
env = user_info['env']
st.session_state['env'] = env

##################### LANGUAGE  #####################

c_1, c_2, c_3 = st.columns([1.5, 4.5, 1], gap="small")

with c_1:
    st.image(logo_image)

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

# st.subheader(translate("dashboards",lang), anchor=False)
st.markdown(f'{translate("requested_by",lang)}<a style="color:blue;font-size:18px;">{""+email+""}</a> | <a style="color:blue;font-size:16px;" target="_self" href="/"> {translate("logout",lang)}</a>', unsafe_allow_html=True)
st.markdown('')
st.markdown('')

######################## Listado de Tableros ########################


# Función para obtener la codificación base64 de una imagen
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Función para crear un HTML para la imagen sin un enlace
def image_without_link(path, width=300, height=150):
    base64_image = get_image_base64(path)
    html = f'<img src="data:image/png;base64,{base64_image}" width="{width}" height="{height}" style="object-fit: cover; border-radius: 10px;"/>'
    return html

######################## Tablero de Lotes ########################

with st.container(border=True):
    c_1, c_2, c_3 = st.columns([4, 0.5, 8])

    with c_1:
        image_path_lyc = 'assets/image_lyc.png'
        # st.markdown(image_without_link(image_path_lyc), unsafe_allow_html=True)
        st.image(Image.open(image_path_lyc))

    with c_3:
        st.page_link("pages/1_Fields_and_Crops.py", label=translate("title", lang))
        # st.write(translate("fields_and_crops_dashboard_description", lang))
        # url_ver_mas = "https://support.geoagro.com/es/kb/"
        # st.markdown(f'[{translate("ver_mas", lang)}]({url_ver_mas})', unsafe_allow_html=True)
        descripcion = translate("fields_and_crops_dashboard_description", lang)
        texto_ver_mas = translate("ver_mas", lang)
        url_ver_mas = "https://support.geoagro.com/es/kb/"

        # Usar st.markdown para combinar la descripción y el enlace "ver más" en la misma línea
        st.markdown(f'{descripcion} [{texto_ver_mas}]({url_ver_mas})', unsafe_allow_html=True)


######################## Tablero de Rindes ########################

with st.container(border=True):
    c_1, c_2, c_3 = st.columns([4, 0.5, 8])

    with c_1:
        image_tablero_yield = 'assets/image_yield.png'
        # st.markdown(image_without_link(image_tablero_yield), unsafe_allow_html=True)
        st.image(Image.open(image_tablero_yield))

    with c_3:
        st.page_link("pages/2_Yields.py", label=translate("title_yield", lang))
        descripcion = translate("proximamente", lang) # translate("yield_dashboard_description", lang)
        texto_ver_mas = '' # translate("ver_mas", lang)
        url_ver_mas = "https://support.geoagro.com/es/kb/"

        # Usar st.markdown para combinar la descripción y el enlace "ver más" en la misma línea
        st.markdown(f'{descripcion} [{texto_ver_mas}]({url_ver_mas})', unsafe_allow_html=True)
