import streamlit as st
import pandas as pd
import time
from passing_stats import obtener_stats_nfl_live  

def cargar_estilos_css():
    st.markdown("""
        <style>
        /* 1. Fondo principal y del sidebar */
        .stApp {
            background-color: white;
            color: #ffffff;
        }
                
                
        .stMarkdown p {
                text-align: center;
                }
        
        /* 2. Estilo de las Tarjetas de Métricas (KPIs) */
        [data-testid="stMetric"] {
            background-color: #ffb330; 
            border: 5px solid #ffb330; 
            padding: 5px;
            border-radius: 8px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
            color: white;
            text-align: center;
        }
            
                
        [data-testid="stHorizontalBlock"]{
                color:white;
                }
                
        label {
                text-align:center
                }
                
        div {
            font-size: 30px;       
            color: black;
            font-weight: 800;
                }
        
        /* 3. Títulos y Cabeceras */
        h1 {
            color: black !important;
            text-transform: uppercase;
            font-weight: 800 !important;
            text-align: center;
        }
        h2, h3 {
            color: black !important; 
        }

        /* 4. Botón de Actualizar */
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

        /* 5. Tablas */
        [data-testid="stDataFrame"] {
            border: 1px solid #374151;
            border-radius: 10px;
        }
                
        [data-testid="stSidebar"] {
            background-color : #ffb330; 
        }
                                
        </style>
    """, unsafe_allow_html=True)

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="NFL Stats 2025 Live",
    page_icon="🏈",
    layout="wide"
)

#Cargar estilos 

cargar_estilos_css()

# TÍTULO Y ESTILO
st.title("NFL 2025 - Passing Leaders Live Tracker")
st.markdown("ARRIBA LA FLY ZONE")

# CARGA DE DATOS CON CACHÉ 
@st.cache_data(show_spinner=False)
def cargar_datos():
    df = obtener_stats_nfl_live()
    return df

# ACTUALIZAR DATOS
if st.button("🔄 Actualizar Datos"):
    st.cache_data.clear() 
    st.rerun()             

# 5. CARGAR Y MOSTRAR DATOS
with st.spinner('Extrayendo datos de la NFL... por favor espera...'):
    df = cargar_datos()

if df is not None:
    # MÉTRICAS PRINCIPALES 

    col1, col2, col3, col4, col5, col6,  = st.columns(6)
    
    leader_yds = df.iloc[0] # El primero de la lista (ya está ordenado por yardas)
    
    col1.metric("Líder en Yardas", leader_yds['Player'])
    col2.metric("Yds", f"{leader_yds['Yds']} Yds" )
    col3.metric("Touchdowns (TD)", int(leader_yds['TD']))
    col4.metric("Equipo", leader_yds['Tm'])
    col5.metric("Rating", leader_yds['Rate'])
    col6.metric("Average", f'{leader_yds['Yds'] / leader_yds['G']} yds')


    st.divider()

    # --- FILTROS INTERACTIVOS ---
    # Barra lateral para filtrar por equipo
    df = df.dropna(subset=['Tm'])
    
    # Asegurarse de que todo sea texto 
    df['Tm'] = df['Tm'].astype(str)

    df = df[~df['Tm'].str.contains("2TM", na=False)]

    # Ordenar
    equipos = sorted(df['Tm'].unique())
    # ----------------------------

    equipo_seleccionado = st.sidebar.multiselect("Filtrar por Equipo:", equipos)
    
    if equipo_seleccionado:
        df_display = df[df['Tm'].isin(equipo_seleccionado)]
    else:
        df_display = df 

  


    # --- VISUALIZACIÓN GRÁFICA ---
    st.subheader("Yardas vs Touchdowns")
    
    # Gráfico de barras
    st.bar_chart(
        df_display,
        x='Yds',
        y='TD',
        color='Tm',
        height=500
    )

    # --- TABLA DE DATOS ---
    st.subheader("NFL Passing Stats 2025")
    st.dataframe(
        df_display, 
        use_container_width=True, 
        hide_index=True
    )

else:
    st.error("Hubo un error al conectar con el servidor de la NFL.")



