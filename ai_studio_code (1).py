import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_zonajobs_limited_run(page_limit=500):
    """
    Versión del scraper que se detiene después de un número limitado de páginas (configurado en 500).
    """
    # --- Configuración de Selenium para entorno sin pantalla ---
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    
    driver = webdriver.Chrome(options=options)
    start_url = 'https://www.zonajobs.com.ar/empleos-publicacion-menor-a-1-mes.html'
    all_jobs = []
    page_count = 1
    
    try:
        driver.get(start_url)
        while True:
            # --- LÍMITE DE PÁGINAS ---
            if page_count > page_limit:
                print(f"\nLímite de {page_limit} páginas alcanzado. Finalizando el scraping.")
                break
            # --------------------------

            print(f"Scrapeando página {page_count}/{page_limit}...")
            # Esperamos a que los avisos sean visibles
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, 'sc-ktBuXk')))
            time.sleep(2) # Pausa para asegurar que todo el JS renderice
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_listings = soup.find_all('div', class_='sc-ktBuXk') # Contenedor estable de cada aviso

            if not job_listings:
                print("No se encontraron más avisos en la página.")
                break

            for job in job_listings:
                try:
                    # Título (buscando la etiqueta <h2>)
                    title_element = job.find('h2')
                    title = title_element.text.strip() if title_element else 'N/A'
                    
                    # Empresa (selector estable)
                    company_element = job.find(class_='sc-jiTwWT')
                    company = company_element.text.strip() if company_element else 'N/A'
                    
                    # Detalle del aviso (buscando la etiqueta <p>)
                    detail_element = job.find('p')
                    detail = detail_element.text.strip() if detail_element else 'N/A'
                    
                    # Ubicación y Modo (selectores estables)
                    details = job.find_all(class_='sc-jFpLkX')
                    location = details[0].text.strip() if len(details) > 0 else 'N/A'
                    work_mode = details[1].text.strip() if len(details) > 1 else 'N/A'
                    
                    # Enlace (selector estable)
                    link_element = job.find('a', class_='sc-ertOQY')
                    link = 'https://www.zonajobs.com.ar' + link_element['href'] if link_element and link_element.has_attr('href') else 'N/A'

                    all_jobs.append({
                        'Titulo': title,
                        'Empresa': company,
                        'Detalle': detail,
                        'Ubicacion': location,
                        'Modo de Trabajo': work_mode,
                        'Enlace': link
                    })
                except Exception as e:
                    print(f"Error parseando un aviso, continuando... Error: {e}")
            
            print(f"Se encontraron {len(job_listings)} avisos en la página {page_count}.")

            # Paginación (selector estable)
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'a.sc-LAuEU.hXefkh')
                driver.execute_script("arguments[0].click();", next_button)
                page_count += 1
                time.sleep(3) # Espera a que la nueva página cargue
            except Exception:
                print("No se encontró el botón 'Siguiente'. Es la última página.")
                break
    except Exception as e:
        print(f"Ocurrió un error principal durante el scraping: {e}")
    finally:
        driver.quit()
        
    return all_jobs

if __name__ == "__main__":
    # Cambiamos el límite aquí
    page_limit_for_run = 500
    print(f"Iniciando Web Scraping (límite de {page_limit_for_run} páginas)...")
    jobs_data = scrape_zonajobs_limited_run(page_limit=page_limit_for_run)
    
    if jobs_data:
        df = pd.DataFrame(jobs_data)
        # Cambiamos el nombre del archivo de salida
        output_filename = f'base_zonajobs_{page_limit_for_run}_paginas.csv'
        df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"\n¡Éxito! Se han exportado {len(jobs_data)} ofertas a '{output_filename}'")
    else:
        print("\nNo se pudo extraer ningún dato.")