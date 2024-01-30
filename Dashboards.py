# Importar bibliotecas para integración web y Streamlit
import streamlit as st

# Importar bibliotecas para manejo de imágenes
from PIL import Image
import base64
import io

# Importar módulos o paquetes locales
from helper import translate

############################################################################
# Estilo
############################################################################

# Cargar la imagen
page_icon = Image.open("assets/favicon geoagro nuevo-13.png")

st.set_page_config(
    page_title="Dashboards",
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

query = f'''
query MyQuery {{
  get_domain(domainId: {user_info['domainId']}, getBase64Logo: true) {{
    base64Logo
    hasLogo
  }}
}}
'''

# Llamar a la función api_call que está cacheada
data = api_call()

import base64
import io
from PIL import Image, UnidentifiedImageError
import binascii

# Define una imagen predeterminada para usar en caso de error
default_image_path = 'assets/GeoAgro_principal.png'
logo_image = Image.open(default_image_path)  # Se define aquí para asegurar que siempre exista

if data['data']['get_domain']["hasLogo"]:
    base64_logo = data['data']['get_domain']['base64Logo']

    # Eliminar la cadena de prefijo si está presente
    prefix = "data:image/png;base64,"
    if base64_logo.startswith(prefix):
        base64_logo = base64_logo.replace(prefix, "", 1)

    # Añadir padding si es necesario
    padding = 4 - len(base64_logo) % 4
    if padding:
        base64_logo += "=" * padding

    try:
        # Decodificar el string base 64
        logo_bytes = base64.b64decode(base64_logo)

        # Crear un objeto de imagen
        logo_image = Image.open(io.BytesIO(logo_bytes))
    except (binascii.Error, UnidentifiedImageError) as e:
        print(f"Error al manejar la imagen: {e}")
        # Se mantiene la imagen predeterminada en caso de error

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
        st.subheader(translate("title", lang))
        st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam condimentum interdum diam vitae hendrerit. Vivamus non nibh massa.")
        url_ver_mas = "https://support.geoagro.com/es/kb/"
        st.markdown(f'[{translate("ver_mas", lang)}]({url_ver_mas})', unsafe_allow_html=True)

######################## Tablero de Rindes ########################

with st.container(border=True):
    c_1, c_2, c_3 = st.columns([4, 0.5, 8])

    with c_1:
        image_tablero_yield = 'assets/image_yield.png'
        # st.markdown(image_without_link(image_tablero_yield), unsafe_allow_html=True)
        st.image(Image.open(image_tablero_yield))

    with c_3:
        st.subheader(translate("title_yield", lang))
        st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam condimentum interdum diam vitae hendrerit. Vivamus non nibh massa.")
        url_ver_mas = "https://support.geoagro.com/es/kb/"
        st.markdown(f'[{translate("ver_mas", lang)}]({url_ver_mas})', unsafe_allow_html=True)
