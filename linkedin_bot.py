import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load saved credentials from json
def load_credentials():
    with open('credentials.json', 'r') as f:
        credentials = json.load(f)
    return credentials

def start_bot(credentials):
    try:
        email = credentials['email']
        password = credentials['password']
        search_query = credentials['search_query']
        max_connections = credentials['max_connections']

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("detach", True)

        service = Service("chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15)

        driver.get("https://www.linkedin.com/login")

        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys(email)

        pwd = driver.find_element(By.ID, "password")
        pwd.send_keys(password)
        pwd.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']")))

        search_box = driver.find_element(By.XPATH, "//input[@placeholder='Search']")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        people_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'People')]")))
        people_tab.click()

        time.sleep(3)

        connection_count = 0

        while connection_count < int(max_connections):
            buttons = driver.find_elements(By.XPATH, "//button")

            for button in buttons:
                try:
                    btn_text = button.text.strip()
                    if btn_text == "Connect":
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1)

                        try:
                            send_wo_note = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send without a note']"))
                            )
                            send_wo_note.click()
                            connection_count += 1
                            time.sleep(1)

                            # NOW check for invitation limit popup
                            try:
                                got_it_button = driver.find_element(By.XPATH, "//button[contains(., 'Got it')]")
                                if got_it_button.is_displayed():
                                    got_it_button.click()
                                    print("Weekly invitation limit reached. Closing browser.")
                                    driver.quit()
                                    return
                            except:
                                pass

                        except:
                            pass

                        if connection_count >= int(max_connections):
                            break

                    time.sleep(2)
                except:
                    continue


            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
                )
                next_button.click()
                time.sleep(2)
            except:
                break

        driver.quit()

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

# Main entry point
if __name__ == "__main__":
    credentials = load_credentials()
    start_bot(credentials)
