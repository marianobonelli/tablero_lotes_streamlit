    ############################################################################
    # timeline
    ############################################################################

    # import streamlit as st
    # from streamlit_timeline import timeline
    # import pandas as pd
    # import json

    # # Convertir las fechas al formato ISO 8601 y manejar valores nulos
    # filtered_df['crop_date'] = pd.to_datetime(filtered_df['crop_date'], errors='coerce')  # Convertir a datetime y manejar errores
    # filtered_df.dropna(subset=['crop_date'], inplace=True)  # Eliminar filas donde 'crop_date' es NaN
    # filtered_df['crop_date'] = filtered_df['crop_date'].dt.strftime('%Y-%m-%d')  # Convertir fechas a cadena

    # # Agrupar por fecha y consolidar los nombres de los lotes en una lista para cada fecha
    # grouped_df = filtered_df.groupby('crop_date')['field_name'].apply(list).reset_index(name='lot_names')

    # # Transformar los datos agrupados del DataFrame a la estructura JSON de TimelineJS
    # def transform_to_timeline_format(df):
    #     events = []
    #     for _, row in df.iterrows():
    #         lot_names_html = '<ul>' + ''.join(f'<li>{name}</li>' for name in row['lot_names']) + '</ul>'
    #         event = {
    #             "start_date": {
    #                 "year": row["crop_date"].split('-')[0],
    #                 "month": row["crop_date"].split('-')[1],
    #                 "day": row["crop_date"].split('-')[2],
    #             },
    #             "text": {
    #                 "headline": f"Lotes",
    #                 "text": f"<p></p>{lot_names_html}"
    #             }
    #             # Puedes agregar la sección de 'media' si es necesario
    #         }
    #         events.append(event)

    #     timeline_json = {
    #         "title": {
    #             "media": {
    #                 "url": "",  # URL a una imagen o video para el título si es necesario
    #                 "caption": "",
    #                 "credit": ""
    #             },
    #             "text": {
    #                 "headline": "Título Principal de la Línea de Tiempo",
    #                 "text": "<p>Descripción de la línea de tiempo aquí.</p>"
    #             }
    #         },
    #         "events": events
    #     }

    #     return timeline_json

    # # Generar la estructura de datos para la línea de tiempo
    # timeline_data = transform_to_timeline_format(grouped_df)

    # # Renderizar la línea de tiempo
    # timeline(timeline_data, height=500)

    ############################################################################

    # # Suponiendo que filtered_df es tu DataFrame
    # # Asegurándonos de que 'crop_date' está en formato de fecha
    # filtered_df['crop_date'] = pd.to_datetime(filtered_df['crop_date'])

    # # Ordenamos primero por fecha y luego por el valor seleccionado
    # filtered_df = filtered_df.sort_values(['crop_date', selected_value])

    # # Agregamos una nueva columna que cuenta la ocurrencia de cada capa por fecha
    # filtered_df['layer_count'] = filtered_df.groupby('crop_date').cumcount() + 1

    # st.markdown('')
    # st.markdown(f"<b>{translate('hectares_by', lang)} {selected_key}</b>", unsafe_allow_html=True)

    # # Crear un gráfico de puntos interactivo con Plotly
    # fig = px.scatter(
    #     filtered_df,
    #     x='crop_date',      # Fecha de cosecha como eje X
    #     y='layer_count',    # Contador de capas como eje Y
    #     color=selected_value,  # Color de los puntos según la selección
    #     labels={'crop_date': 'Fecha de Cosecha', 'layer_count': 'Número de Capa', selected_value: selected_key},
    #     height=300,
    #     color_discrete_sequence=selected_colors  # Paleta de colores
    # )

    # # Crear el hovertemplate personalizado
    # hovertemplate = (
    #     f"<b>%{{x}}</b><br>"
    #     f"Número de Capa: %{{y}}<br>"
    #     f"{selected_key}: %{{{selected_value}}}<br>"
    # )

    # # Aplicar el hovertemplate y datos personalizados al gráfico
    # fig.update_traces(hovertemplate=hovertemplate)

    # # Personalizar la fuente del hoverlabel y el diseño del gráfico
    # fig.update_layout(
    #     hoverlabel=dict(
    #         bgcolor="white",
    #         font_size=12,
    #         font_family="Roboto"
    #     ),
    #     font=dict(
    #         family="Roboto",
    #         size=18,
    #     ),
    #     xaxis_title='Fecha de Cosecha',
    #     yaxis_title='Número de Capa',
    #     xaxis_tickangle=-45,
    #     xaxis=dict(
    #         type='date'  # Esto hace que el eje X se trate como fechas
    #     ),
    #     yaxis=dict(
    #     showgrid=False,  # Esto oculta las líneas horizontales de la cuadrícula
    #     showticklabels=False  # Esto oculta las etiquetas del eje Y
    #     ),
    # )
    

    # # Mostrar el gráfico en Streamlit
    # st.plotly_chart(fig, use_container_width=True)
