import os
import csv

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def take_element_screenshot(driver, locator,path):
    wait = WebDriverWait(driver, 10)

    element = wait.until(EC.visibility_of_element_located(locator))

    driver.execute_script("arguments[0].scrollIntoView(true);", element)

    element.screenshot(path)

    

class SeleniumWebDriverContextManager:
    def __init__(self):
        self.driver: WebDriver = None

    def __enter__(self) -> WebDriver:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")

        chrome_options.add_argument("--allow-file-access-from-files")

        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()

def extract_table(driver: WebDriver, output_path: str):
    wait = WebDriverWait(driver, 10)

    try:
        table = wait.until(
            EC.presence_of_element_located((By.ID, "results-table"))
        )
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

        data = []
        for row in rows:
            cols = row.find_elements(By.XPATH, ".//td")
            if cols:
                row_data = [col.text.strip() for col in cols]
                data.append(row_data)
        
        if not data:
            print("No data found in the table.")
            return
        
    
        header = ["Result","Test","Duration","Links"]
        with open(output_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(data)
        print(f"Table saved to {output_path}")
    except TimeoutException:
        print("Timed out waiting for the table to load.")
    except NoSuchElementException:
        print("Table element not found on the page.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def extract_and_save_chart_data(driver: WebDriver, output_file: str):
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "#results-table tbody tr")

        if not rows:
            print("No rows found for chart data extraction.")
            return
        aggregation = {}
        for row in rows:
            cols = row.find_elements(By.XPATH, ".//td")
            if len(cols) >= 3:
                result = cols[0].text.strip()
                duration_text = cols[2].text.strip()
                
                duration = int(duration_text.replace("ms", "").strip())
                if result not in aggregation:
                    aggregation[result] = []
                aggregation[result].append(duration)

        final_data = [[key,min(values)] for key, values in aggregation.items()]

        with open(output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Result", "Min Duration (ms)"])
            writer.writerows(final_data)
        print(f"Chart data saved to {output_file}")
    except Exception as e:
        print(f"Data extracting failed: {e}")



def process_doughnut_chart(driver: WebDriver, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    wait = WebDriverWait(driver, 10)

    try:
        filters = driver.find_elements(By.CSS_SELECTOR, "input.filter")

        if not filters:
            print("No filters found on the page.")
            return
        active_filters = [f for f in filters if f.is_enabled()]
        print(f"Found {len(active_filters)} active filters.")

        screenshot_index = 0
        csv_index = 0

        take_element_screenshot(driver, (By.ID, "results-table"), f"{output_dir}/screenshot{screenshot_index}.png")
        screenshot_index += 1
        take_element_screenshot(driver,(By.CLASS_NAME,"summary"),f"{output_dir}/screenshot{screenshot_index}.png")
        screenshot_index += 1
        take_element_screenshot(driver,(By.CLASS_NAME,"filters"),f"{output_dir}/screenshot{screenshot_index}.png")
        screenshot_index += 1

        extract_and_save_chart_data(driver, f"{output_dir}/doughnut{csv_index}.csv")
        csv_index += 1


        for checkbox in active_filters:
            try:
                driver.execute_script("arguments[0].click();", checkbox)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#results-table tbody"))
                           )
                take_element_screenshot(driver, (By.ID, "results-table"), f"{output_dir}/screenshot{screenshot_index}.png")
                screenshot_index += 1

                extract_and_save_chart_data(driver, f"{output_dir}/doughnut{csv_index}.csv")
                csv_index += 1
            except Exception as e:
                print(f"Filter click failed: {e}")
        print("Done.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    with SeleniumWebDriverContextManager() as driver:
        file_path = os.path.abspath("report.html")
        driver.get(f"file:///{file_path}")
        
        extract_table(driver, "table.csv")

        process_doughnut_chart(driver, "doughnut_charts")
