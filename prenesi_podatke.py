from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# -------- Nastavitve --------
chromedriver_path = "/pot/do/chromedriver"  # spremeni na lokacijo chromedriver na tvojem računalniku
base_url = "https://meteo.arso.gov.si/met/sl/app/webmet/#webmet==wL1BHbvFGZz9SblRXZv9SYwB3L3VmYtVGdvAXdqN3LwJ3bn9iclFGbt9ydlFGdoVmcvkmbpRnL41Gb8xHf;"

# Seznam postaj (ime, id) - ID moraš dobiti iz ARSO arhiva
stations = [
    ("Ljubljana Bežigrad", "01260"),
    ("Novo Mesto", "01560"),
    ("Murska Sobota", "07060"),
    ("Portorož letališče", "09010"),
    ("Bilje", "10030"),
    ("Kredarica", "00240"),
    ("Maribor", "03160"),
    ("Celje Medlog", "03330")
]

# Datum začetka in konca
dates = pd.date_range("2024-01-01", "2024-12-31")

# -------- Inicializacija brskalnika --------
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # brez GUI, če hočeš videti, odstrani
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

all_data = []

try:
    for date in dates:
        print(f"Obdelujem datum: {date.date()}")
        driver.get(base_url)
        time.sleep(3)  # počakaj, da se stran naloži

        for station_name, station_id in stations:
            try:
                # Poišči izbiro postaje in datum
                # --- To bo odvisno od dejanskega HTML-ja, spodaj je primer ---
                # Izberi postajo
                select_station = Select(driver.find_element(By.ID, "stationSelect"))
                select_station.select_by_value(station_id)
                # Izberi datum
                date_input = driver.find_element(By.ID, "dateInput")
                date_input.clear()
                date_input.send_keys(date.strftime("%Y-%m-%d"))
                # Pritisni gumb za prikaz podatkov
                driver.find_element(By.ID, "showDataBtn").click()
                
                # Počakaj, da se tabela naloži
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "dataTable"))
                )

                # Preberi tabelo
                table = driver.find_element(By.ID, "dataTable")
                rows = table.find_elements(By.TAG_NAME, "tr")
                row_data = {"Datum": date.date(), "Postaja": station_name}

                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) == 2:
                        key = cols[0].text.strip()
                        value = cols[1].text.strip()
                        row_data[key] = value

                all_data.append(row_data)

            except Exception as e:
                print(f"Napaka pri {station_name} {date.date()}: {e}")

finally:
    driver.quit()

# Shrani vse v CSV
df = pd.DataFrame(all_data)
df.to_csv("ARSO_2024_data.csv", index=False)
print("Podatki shranjeni v ARSO_2024_data.csv")
