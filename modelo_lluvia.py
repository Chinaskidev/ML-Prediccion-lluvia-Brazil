import pandas as pd
import streamlit as st
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta


st.set_page_config(page_title='Predicciones Rio Grande do Sul', page_icon = ':cloud :', layout = 'centered')

# aca se carga la API
load_dotenv()
api_key = os.getenv('API_KEY')

# Función para obtener datos climáticos desde OpenWeather
def obtener_datos_horarios(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        processed_data = []
        for item in data['list']:
            precip_mm = item.get('rain', {}).get('3h', 0) if isinstance(item.get('rain', {}), dict) else 0
            processed_data.append({
                'Hora': datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d %H:%M:%S'),
                'Temperatura': item['main']['temp'],
                'Humedad': item['main']['humidity'],
                'Velocidad Viento': item['wind']['speed'],
                'Dirección del viento': item['wind']['deg'],
                'Precipitación (mm/3h)': precip_mm,
                'Condiciones': item['weather'][0]['description'].capitalize()
            })
        return pd.DataFrame(processed_data)
    else:
        st.error(f"No se pudo obtener datos del clima. Código de estado: {response.status_code}, Mensaje: {response.text}")
        return None

# Convertir la dirección del viento de grados a cardinales
def convertir_direccion_viento(deg):
    if deg >= 337.5 or deg < 22.5:
        return 'N'
    elif deg >= 22.5 and deg < 67.5:
        return 'NE'
    elif deg >= 67.5 and deg < 112.5:
        return 'E'
    elif deg >= 112.5 and deg < 157.5:
        return 'SE'
    elif deg >= 157.5 and deg < 202.5:
        return 'S'
    elif deg >= 202.5 and deg < 247.5:
        return 'SW'
    elif deg >= 247.5 and deg < 292.5:
        return 'W'
    elif deg >= 292.5 and deg < 337.5:
        return 'NW'

# Obtener la imagen adecuada para el clima y el texto descriptivo
def obtener_imagen_clima(condiciones):
    condiciones = condiciones.lower()
    if 'rain' in condiciones:
        return './img/lluvia.png', 'Va a llover, protégete y lleva paraguas'
    elif 'few clouds' in condiciones:
        return './img/soleado.png', 'Hará sol, ponte bloqueador y bebe mucha agua'
    elif 'scattered clouds' in condiciones:
        return './img/nubes_dispersas.png', 'Estará nublado, ponte un abrigo si sales'
    elif 'moderate rain' in condiciones:
        return './img/lluvia_moderada.png', 'Va a haber algo de lluvia, lleva paraguas'
    elif 'heavy intensity rain' in condiciones:
        return './img/tormenta.png', 'Habrá tormenta, toma precauciones'
    elif 'overcast clouds' in condiciones:
        return './img/nublado.png', 'Estará completamente nublado'
    else:
        return './img/soleado.png', 'Soleado, Relajate'

# Coordenadas del centro del estado de Río Grande del Sur
lat = -29.75
lon = -53.15

# Título centrado
st.markdown("<h1 style='text-align: center; color: #b6bbb5'>Predicción de Clima en Río Grande del Sur</h1>", unsafe_allow_html=True)

# Selector de fecha en la barra lateral
st.sidebar.header("Selecciona la fecha para la predicción")
fecha = st.sidebar.date_input("Fecha", datetime.now() + timedelta(days=1))

# Obtener datos climáticos de OpenWeather
clima_df = obtener_datos_horarios(lat, lon, api_key)

if clima_df is not None:
    # Convertir la dirección del viento de grados a cardinales
    clima_df['Dirección del viento'] = clima_df['Dirección del viento'].apply(convertir_direccion_viento)

    # Filtrar datos para la fecha seleccionada
    clima_df['Fecha'] = pd.to_datetime(clima_df['Hora']).dt.date
    fecha_seleccionada = pd.to_datetime(fecha).date()
    clima_df = clima_df[clima_df['Fecha'] == fecha_seleccionada]

    # Mostrar resultados generales
    st.subheader(f"Condiciones Climáticas para {fecha.strftime('%A, %d de %B de %Y')}")
    
    # Seleccionar una fila para obtener la imagen del clima y el texto descriptivo
    if not clima_df.empty:
        condiciones = clima_df.iloc[0]['Condiciones']
        imagen_clima, texto_clima = obtener_imagen_clima(condiciones)
        st.image(imagen_clima, caption=texto_clima, use_column_width=True)
    else:
        st.write("No hay datos disponibles para la fecha seleccionada.")

    # Mostrar datos horarios en una tabla
    st.subheader("Datos Horarios")
    clima_df_horario = clima_df[['Hora', 'Temperatura', 'Humedad', 'Velocidad Viento', 'Dirección del viento', 'Precipitación (mm/3h)']]
    clima_df_horario.rename(columns={
        'Hora': 'Hora',
        'Temperatura': 'Temperatura (°C)',
        'Humedad': 'Humedad (%)',
        'Velocidad Viento': 'Velocidad del Viento (km/h)',
        'Dirección del viento': 'Dirección del Viento',
        'Precipitación (mm/3h)': 'Precipitación (mm/3h)'
    }, inplace=True)
    st.table(clima_df_horario)
