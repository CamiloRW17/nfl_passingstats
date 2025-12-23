import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import time

# IMPORTS PARA SELENIUM
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def obtener_stats_nfl_live():
    url = "https://www.pro-football-reference.com/years/2025/passing.htm"
    
    print(f"🚀 Iniciando obtención de datos automática {url}")

    # 1. CONFIGURACIÓN DEL NAVEGADOR
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # CHROME AUTOMÁTICO
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # NAVEGAR A LA PÁGINA
        driver.get(url)
        print("⏳ Esperando a que cargue la tabla (3 segundos)...")
        time.sleep(3) # Damos tiempo a que el JavaScript construya la tabla
        
        # EXTRAER EL HTML YA RENDERIZADO
        html_vivo = driver.page_source
        
    except Exception as e:
        print(f"❌ Error en el navegador: {e}")
        driver.quit()
        return None
    

    driver.quit()


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