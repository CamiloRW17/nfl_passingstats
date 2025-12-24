import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import time

# IMPORTS PARA SELENIUM
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import shutil  # Para buscar archivos en el sistema

def obtener_stats_nfl_live():
    url = "https://www.pro-football-reference.com/years/2025/passing.htm"
    
    # 1. OPCIONES DEL NAVEGADOR
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080") # A veces ayuda a que no detecten bot
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # 2. INTELIGENCIA DE UBICACIÓN (LOCAL VS NUBE)
    # Buscamos si existe 'chromium' y 'chromedriver' instalados en el sistema
    chromium_path = shutil.which("chromium") or shutil.which("chromium-browser")
    chromedriver_path = shutil.which("chromedriver")

    if chromium_path and chromedriver_path:
        # ESTAMOS EN LA NUBE (Streamlit Cloud) ☁️
        print(f"☁️ Usando configuración de Nube:\nBrowser: {chromium_path}\nDriver: {chromedriver_path}")
        options.binary_location = chromium_path
        service = Service(executable_path=chromedriver_path)
    else:
        # ESTAMOS EN LOCAL (Tu Mac) 💻
        print("💻 Usando configuración Local (Mac/Windows)")
        # Aquí sí dejamos que el Manager descargue lo que necesite
        service = Service(ChromeDriverManager().install())

    # 3. INICIAR DRIVER
    try:
        driver = webdriver.Chrome(service=service, options=options)
        
        # ... RESTO DE TU LÓGICA DE SIEMPRE ...
        driver.get(url)
        # ... etc ...
        
        # (Asegúrate de pegar aquí el resto de tu función original: BeautifulSoup, Pandas, return df)
        
        # --- EJEMPLO RÁPIDO DE LO QUE SIGUE (NO COPIES ESTO SI YA LO TIENES): ---
        import time
        time.sleep(3)
        html_vivo = driver.page_source
        driver.quit()
        # ... procesamiento pandas ...
        # return df
        # -----------------------------------------------------------------------
        
    except Exception as e:
        print(f"❌ Error crítico iniciando Selenium: {e}")
        return None

    print("Info capturada. Procesando con Pandas...")
    
    soup = BeautifulSoup(html_vivo, 'html.parser')
    tabla = soup.find('table', id='passing')

    if not tabla:
        print("❌ No se encontró la tabla id='passing'.")
        return None

    html_en_memoria = StringIO(str(tabla))
    dfs = pd.read_html(html_en_memoria)
    df = dfs[0]

    # LIMPIEZA DE DATOS (Tu ETL)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0)
        
    df = df[df['Rk'] != 'Rk']
    
    if 'Tm' not in df.columns and 'Team' in df.columns:
        df.rename(columns={'Team': 'Tm'}, inplace=True)

    df['Player'] = df['Player'].str.replace('*', '', regex=False)
    df['Player'] = df['Player'].str.replace('+', '', regex=False)

    columnas_clave = ['Player', 'G', 'Tm', 'Yds', 'TD', 'Int', 'Rate']
    cols_existentes = [c for c in columnas_clave if c in df.columns]
    df_final = df[cols_existentes].copy()

    cols_numericas = ['G','Yds', 'TD', 'Int', 'Rate']
    for col in cols_numericas:
        if col in df_final.columns:
            df_final[col] = pd.to_numeric(df_final[col])

    if 'Yds' in df_final.columns:
        df_final = df_final.sort_values(by='Yds', ascending=False).reset_index(drop=True)
    
    return df_final

if __name__ == '__main__':
    stats = obtener_stats_nfl_live()
    
    if stats is not None:
        print("\n🏆 TOP 5 LÍDERES EN YARDAS (EN VIVO):")
        print(stats.head(5))
        stats.to_csv('nfl_data_live.csv', index=False)
        print("\n✅ Datos guardados en 'nfl_data_live.csv'")