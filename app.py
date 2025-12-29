import streamlit as st
import pandas as pd
from passing_stats import obtener_stats_nfl_live

# Configuración inicial (debe ir al principio)
st.set_page_config(
    page_title="NFL Stats 2025 Live",
    page_icon="🏈",
    layout="wide"
)

# Inyección de CSS para personalizar la UI (KPIs, tablas y botones)
def cargar_estilos_css():
    st.markdown("""
        <style>
        .stApp { background-color: white; color: #ffffff; }
        .stMarkdown p { text-align: center; }
        
        /* Estilo tarjeta para las métricas */
        [data-testid="stMetric"] {
            background-color: #ffb330; 
            border: 5px solid #ffb330; 
            padding: 5px;
            border-radius: 8px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
            color: white;
            text-align: center;
        }
        [data-testid="stHorizontalBlock"]{ color: white; }
        label { text-align: center; }
        div { font-size: 30px; color: black; font-weight: 800; }
        
        h1 { color: black !important; text-transform: uppercase; font-weight: 800 !important; text-align: center; }
        h2, h3 { color: black !important; }

        /* Botón con hover effect */
        .stButton > button {
            width: 100%;
            background-color: #598b96; 
            color: white;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #00b03b; 
            transform: scale(1.02);
            color: black;
        }

        [data-testid="stDataFrame"] { border: 1px solid #374151; border-radius: 10px; }
        [data-testid="stSidebar"] { background-color : #ffb330; }
        </style>
    """, unsafe_allow_html=True)

cargar_estilos_css()

st.title("NFL 2025 - Passing Leaders Live Tracker")
st.markdown("ARRIBA LA FLY ZONE")

# Uso de caché para evitar scraping en cada interacción del usuario
@st.cache_data(show_spinner=False)
def cargar_datos():
    return obtener_stats_nfl_live()

# Botón para limpiar caché y forzar nueva extracción de datos
if st.button("🔄 Actualizar Datos"):
    st.cache_data.clear()
    st.rerun()

with st.spinner('Extrayendo datos de la NFL...'):
    df = cargar_datos()

# Validación: Solo renderizamos si el scraper trajo datos
if df is not None:
    
    # --- KPIs Principales ---
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    leader = df.iloc[0]
    # Evitar división por cero si es el inicio de temporada
    avg_yds = leader['Yds'] / leader['G'] if leader['G'] > 0 else 0
    
    col1.metric("Líder en Yardas", leader['Player'])
    col2.metric("Yds", f"{leader['Yds']} Yds")
    col3.metric("Touchdowns (TD)", int(leader['TD']))
    col4.metric("Equipo", leader['Tm'])
    col5.metric("Rating", leader['Rate'])
    col6.metric("Average", f'{avg_yds:.1f} yds/g')

    st.divider()

    # --- Limpieza y Filtros ---
    df = df.dropna(subset=['Tm'])
    df['Tm'] = df['Tm'].astype(str)
    # Filtramos "2TM" (jugadores que cambiaron de equipo) para evitar duplicados en gráficas
    df = df[~df['Tm'].str.contains("2TM", na=False)]

    equipos = sorted(df['Tm'].unique())
    equipo_seleccionado = st.sidebar.multiselect("Filtrar por Equipo:", equipos)
    
    if equipo_seleccionado:
        df_display = df[df['Tm'].isin(equipo_seleccionado)]
    else:
        df_display = df

    # --- Visualización ---
    st.subheader("Análisis: Yardas vs Touchdowns")
    
    st.bar_chart(
        df_display,
        x='Yds',
        y='TD',
        color='Tm',
        height=500
    )

    st.subheader("NFL Passing Stats 2025 - Tabla Detallada")
    st.dataframe(
        df_display, 
        use_container_width=True, 
        hide_index=True
    )

else:
    st.error("Error de conexión con la fuente de datos (NFL). Intenta más tarde.")