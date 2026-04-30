import os
import csv
import time


from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def take_element_screenshot(driver, locator, path):
    wait = WebDriverWait(driver, 10)

    element = wait.until(
        EC.visibility_of_element_located(locator)
    )
    driver.execute_script(
        "arguments[0].scrollIntoView(true);",
        element
    )
    time.sleep(1)
    element.screenshot(path)
    print(f"Screenshot created: {path}")

    

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
        columns = driver.find_elements(By.CSS_SELECTOR, "g.y-column")
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


def wait_for_donut_chart(driver):

    wait = WebDriverWait(driver, 15)

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "g.pielayer")
        )
    )

    wait.until(
        lambda d: len(
            d.find_elements(
                By.CSS_SELECTOR,
                'g.pielayer text.slicetext[data-notex="1"]'
            )
        ) > 0
    )
    time.sleep(1)

def get_legend_items(driver):
    """
    Returns all legend labels + toggle buttons.
    """
    legends = []

    traces = driver.find_elements(
        By.CSS_SELECTOR,
        "g.legend g.traces"
    )

    for trace in traces:

        try:

            label = trace.find_element(
                By.TAG_NAME,
                "text"
            ).text.strip()

            toggle = trace.find_element(
                By.CSS_SELECTOR,
                "rect.legendtoggle"
            )

            legends.append({
                "label": label,
                "toggle": toggle
            })

        except Exception:
            continue

    return legends


def click_legend(driver, element):
    """
    Plotly-safe SVG click.
    """

    driver.execute_script(
        "arguments[0].scrollIntoView(true);",
        element
    )

    time.sleep(0.5)

    driver.execute_script("""
        arguments[0].dispatchEvent(
            new MouseEvent('mousedown', { bubbles: true })
        );

        arguments[0].dispatchEvent(
            new MouseEvent('mouseup', { bubbles: true })
        );

        arguments[0].dispatchEvent(
            new MouseEvent('click', { bubbles: true })
        );
    """, element)

    time.sleep(1)


def extract_donut_data(driver):
    """
    Extract visible doughnut labels and values.
    """

    data = []

    try:

        labels = driver.find_elements(
            By.CSS_SELECTOR,
            'g.pielayer text.slicetext[data-notex="1"]'
        )

        for label in labels:

            tspans = label.find_elements(
                By.TAG_NAME,
                "tspan"
            )

            if len(tspans) >= 2:

                facility_type = tspans[0].text.strip()
                value = tspans[1].text.strip()

                data.append([
                    facility_type,
                    value
                ])

    except Exception as e:

        print(f"Data extraction failed: {e}")

    return data


def save_donut_csv(data, index, output_dir):

    path = os.path.join(
        output_dir,
        f"doughnut{index}.csv"
    )

    with open(path, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            "Facility Type",
            "Min Average Time Spent"
        ])

        writer.writerows(data)

    print(f"CSV created: {path}")


def set_active_filters(driver, active_labels):
    """
    Set chart state to match desired active labels.
    """

    legends = get_legend_items(driver)
    for legend in legends:
        try:
            click_legend(driver, legend["toggle"])
        except Exception as e:
            print(f"Error clicking legend '{legend['label']}': {e}")
    time.sleep(1.5)

    for legend in legends:
        if legend["label"] in active_labels:
            try:
                click_legend(driver, legend["toggle"])
            except Exception as e:
                print(f"Error clicking legend '{legend['label']}': {e}")
    time.sleep(1.5)

def apply_filters_from_clean_state(driver, active_labels):

    legends = get_legend_items(driver)

    for legend in legends:
        label = legend["label"]

        if label in active_labels:
            try:
                click_legend(driver, legend["toggle"])
            except Exception as e:
                print(f"Error clicking legend '{label}': {e}")
    time.sleep(1.5)

def process_doughnut_chart(driver, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    #wait_for_donut_chart(driver)

    scenarios = [
        ["Hospital", "Specialty Center", "Clinic"],
        ["Hospital", "Clinic"],
        ["Clinic"],
        []
    ]

    for index, active_labels in enumerate(scenarios):

        print("\n====================")
        print(f"Scenario {index}")
        print(f"Active filters: {active_labels}")

        try:
            driver.refresh()
            wait_for_donut_chart(driver)

            apply_filters_from_clean_state(driver, active_labels)
            time.sleep(2)

            screenshot_path = os.path.join(
                output_dir,
                f"screenshot{index}.png"
            )

            take_element_screenshot(
                driver,
                (By.CSS_SELECTOR, ".js-plotly-plot"),
                screenshot_path
            )

            data = extract_donut_data(driver)

            save_donut_csv(
                data,
                index,
                output_dir
            )

        except Exception as e:

            print(f"Scenario {index} failed: {e}")
    print("\nDoughnut chart scenarios completed")

if __name__ == "__main__":
    with SeleniumWebDriverContextManager() as driver:
        file_path = os.path.abspath("report.html")
        driver.get(f"file:///{file_path}")
        
        extract_table(driver, "table.csv")

        process_doughnut_chart(driver, "doughnut_charts")
