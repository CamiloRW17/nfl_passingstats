import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import time
import shutil  

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def obtener_stats_nfl_live():
    url = "https://www.pro-football-reference.com/years/2025/passing.htm"
    
    # --- 1. CONFIGURACIÓN DEL NAVEGADOR (HEADLESS) ---
    # Estas opciones son críticas para evitar crasheos en entornos de servidor (Docker/Streamlit)
    options = Options()
    options.add_argument("--headless") # Ejecuta sin interfaz gráfica (más rápido y compatible)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080") 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # --- 2. DETECCIÓN DE ENTORNO (HÍBRIDO) ---
    # Lógica inteligente para alternar entre entorno Local (WebDriverManager) y Nube (Binarios de Linux).
    # Esto permite que el mismo código funcione en mi Mac y en el servidor de Streamlit sin cambios.
    chromium_path = shutil.which("chromium") or shutil.which("chromium-browser")
    chromedriver_path = shutil.which("chromedriver")

    if chromium_path and chromedriver_path:
        print(f"☁️ Usando configuración de Nube (Linux detectado)")
        options.binary_location = chromium_path
        service = Service(executable_path=chromedriver_path)
    else:
        print("💻 Usando configuración Local (Mac/Windows)")
        service = Service(ChromeDriverManager().install())

    # --- 3. EXTRACCIÓN DE DATOS (SCRAPING) ---
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        # Espera explícita para asegurar carga de JS si fuera necesario
        time.sleep(3)
        html_vivo = driver.page_source
        driver.quit() # Cerramos navegador para liberar memoria RAM
        
    except Exception as e:
        print(f"❌ Error crítico iniciando Selenium: {e}")
        return None

    print("Info capturada. Procesando con Pandas...")
    
    # --- 4. PARSEO Y LIMPIEZA (PANDAS & BS4) ---
    # Usamos BeautifulSoup para aislar la tabla antes de pasarla a Pandas (más robusto)
    soup = BeautifulSoup(html_vivo, 'html.parser')
    tabla = soup.find('table', id='passing')

    if not tabla:
        print("❌ No se encontró la tabla de estadísticas.")
        return None

    html_en_memoria = StringIO(str(tabla))
    dfs = pd.read_html(html_en_memoria)
    df = dfs[0]

    # Limpieza de Headers: Si hay multi-index, lo aplanamos
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0)
        
    # Filtrado de basura: Eliminamos las filas repetidas que usa la web como separadores
    df = df[df['Rk'] != 'Rk']
    
    # Normalización de nombres
    if 'Tm' not in df.columns and 'Team' in df.columns:
        df.rename(columns={'Team': 'Tm'}, inplace=True)

    # Limpieza de strings: Quitamos caracteres especiales de los nombres (*, +)
    df['Player'] = df['Player'].str.replace('*', '', regex=False)
    df['Player'] = df['Player'].str.replace('+', '', regex=False)

    # Selección de columnas relevantes para el dashboard
    columnas_clave = ['Player', 'G', 'Tm', 'Yds', 'TD', 'Int', 'Rate']
    cols_existentes = [c for c in columnas_clave if c in df.columns]
    df_final = df[cols_existentes].copy()

    # Conversión de tipos: De string a numeric para poder ordenar y graficar
    cols_numericas = ['G','Yds', 'TD', 'Int', 'Rate']
    for col in cols_numericas:
        if col in df_final.columns:
            df_final[col] = pd.to_numeric(df_final[col])

    # Ordenamiento final
    if 'Yds' in df_final.columns:
        df_final = df_final.sort_values(by='Yds', ascending=False).reset_index(drop=True)
    
    return df_final

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == '__main__':
    stats = obtener_stats_nfl_live()
    
    if stats is not None:
        print("\n🏆 TOP 5 LÍDERES EN YARDAS (EN VIVO):")
        print(stats.head(5))
        stats.to_csv('nfl_data_live.csv', index=False)
        print("\n✅ Datos guardados exitosamente.")