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
    wait = WebDriverWait(driver, 15)

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "g.table")))

        wait.until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "g.y-column")) > 0)
        wait.until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "g.column-cell text.cell-text")) > 0)
        import time

        time.sleep(1.5)  # stabilize SVG rendering (important for D3/Plotly)

        header_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "g.y-column g#header text.cell-text"
        )
        headers = [h.text.strip() for h in header_elements]

        # 4. get all columns
        columns = driver.find_elements(By.CSS_SELECTOR, "g.y-column")

        # 5. build column data matrix first
        column_matrix = []

        for col in columns:
            cells = col.find_elements(
                By.CSS_SELECTOR,
                "g.column-cell text.cell-text"
            )

            col_values = []
            for c in cells:
                txt = c.text.strip()
                if txt:
                    col_values.append(txt)

            column_matrix.append(col_values)
        max_len = max(len(col) for col in column_matrix)

        for col in column_matrix:
            col.extend([""] * (max_len - len(col)))
        rows = list(zip(*column_matrix))

        clean_rows = []
        header_set = set(headers)

        for row in rows:
            if set(row) == header_set:
                continue

            clean_rows.append(row)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(clean_rows)

        print(f"Table successfully extracted to {output_path}")

    except Exception as e:
        print(f"FAILED extraction: {type(e).__name__}: {e}")
        raise

def extract_and_save_chart(driver,index, output_dir):
    try:
        slices = driver.find_elements(By.CSS_SELECTOR, "g.slice")

        if not slices:
            print("No slices found")
            return

        file_path = os.path.join(output_dir, f"doughnut{index}.csv")

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Facility Type", "Min Average Time Spent"])

            for s in slices:
                tspans = s.find_elements(By.TAG_NAME, "tspan")

                if len(tspans) >= 2:
                    label = tspans[0].text.strip()
                    value = tspans[1].text.strip()

                    writer.writerow([label, value])

        print(f"{file_path} created")

    except Exception as e:
        print(f"Chart extraction failed: {e}")


def process_doughnut_chart(driver: WebDriver, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    wait = WebDriverWait(driver, 10)

    try:
       chart = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "g.pielayer")))
       driver.execute_script("arguments[0].scrollIntoView(true);", chart)
       chart_path = os.path.join(output_dir, "screenshot0.png")
       chart.screenshot(chart_path)

       extract_and_save_chart(driver,0, output_dir)
       print(f"Doughnut chart screenshot saved to {chart_path}")

    except Exception as e:
        print(f"An error occurred while processing the doughnut chart: {e}")

if __name__ == "__main__":
    with SeleniumWebDriverContextManager() as driver:
        file_path = os.path.abspath("report.html")
        driver.get(f"file:///{file_path}")
        
        extract_table(driver, "table.csv")

        process_doughnut_chart(driver, "doughnut_charts")
