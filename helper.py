#############################
# TRANSLATIONS 
#############################

from language import translate_dict

def translate(string, language):

    try:
        return translate_dict[string][language]
    except:
        return "Unknown"
    
#############################
# API CALL LOGO MARCA BLANCA 
#############################
    
import requests  
from PIL import Image, UnidentifiedImageError
import base64
import io
import binascii
    
def api_call_logo(user_info, access_key_id, default_logo='assets/GeoAgro_principal.png'):

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
    response = requests.post(url, json={'query': query}, headers=headers)

    if response.status_code != 200:
        logo_image = Image.open(default_logo)
        return logo_image

    # Convertir el contenido de la respuesta de JSON a un diccionario
    data = response.json()

    if data and data['data']['get_domain']["hasLogo"]:
        base64_logo = data['data']['get_domain']['base64Logo']
        
        # Dividir en la coma y usar lo que sigue, si es necesario
        if ',' in base64_logo:
            base64_logo = base64_logo.split(',', 1)[1]

        # Añadir padding si es necesario
        padding = 4 - len(base64_logo) % 4
        if padding:
            base64_logo += "=" * padding

        try:
            # Decodificar el string base64
            logo_bytes = base64.b64decode(base64_logo)
            logo_image = Image.open(io.BytesIO(logo_bytes))
            return logo_image
        except (binascii.Error, UnidentifiedImageError) as e:
            print(f"Error al manejar la imagen: {e}")

    return Image.open(default_logo)

#############################
# API CALL FIELDS TABLE 
#############################

import requests
import pandas as pd

def api_call_fields_table(user_info, access_key_id):
    url = 'https://lpul7iylefbdlepxbtbovin4zy.appsync-api.us-west-2.amazonaws.com/graphql'
    headers = {
        'x-api-key': access_key_id,
        'Content-Type': 'application/json'
    }
    query = f'''
    query MyQuery {{
      get_field_table(domainId: {user_info['domainId']}, email: "{user_info['email']}", exportAllAsCsv: true, lang: "{user_info['language']}", withHectares: true, withCentroid: true, withGeom: true, delimiter: ";") {{
        csvUrl
      }}
    }}
    '''
    response = requests.post(url, json={'query': query}, headers=headers)

    if response.status_code != 200:
        return None
    else:
        data = response.json()
        csv_url = data['data']['get_field_table']['csvUrl']

        df = pd.read_csv(csv_url, delimiter=";")
        # Eliminar filas donde 'hectares' es NaN
        df = df.dropna(subset=['hectares'])

        # Eliminar filas donde 'hectares' es igual a 0
        df = df[df['hectares'] != 0]

        return data, df
