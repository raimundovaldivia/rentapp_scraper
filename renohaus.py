from datetime import datetime
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

# import ActionChains
from selenium.webdriver.common.action_chains import ActionChains

import csv


def write_columns_to_csv(filename, list_of_columns):
    """
    Writes a list of lists to a CSV file, where each inner list is a column.

    :param filename: str, the name of the CSV file to create or overwrite.
    :param list_of_columns: list of lists, each inner list represents a column.
    """
    import csv

    # Find the length of the longest column
    max_length = max(len(column) for column in list_of_columns)

    # Open the specified CSV file in write mode
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write each row
        for i in range(max_length):
            row = [column[i] if i < len(
                column) else '' for column in list_of_columns]
            writer.writerow(row)


chromedriver_autoinstaller.install()
ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
driver = webdriver.Chrome()
driver.get("https://mirentapp.app/")
driver.maximize_window()

user_name = driver.find_element(By.ID, "email")
password = driver.find_element(By.ID, "password")

user_name.send_keys("contacto@renohaus.cl")
password.send_keys("Rent7290.")

wait = WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions)
button = driver.find_element(
    By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div/div/div[2]/div[3]/button[2]")
button.click()
time.sleep(15)


scroll_bar_xpath = "/html/body/div[1]/div/div[1]/div[1]/div/div/div/div[1]/div[2]"
element = driver.find_element(By.XPATH, scroll_bar_xpath)

# Do stuff
action = ActionChains(driver)
action.move_to_element(element).move_by_offset(0, 100).click().perform()

# click contavilidad
contabilidad = wait.until(EC.presence_of_element_located((
    By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div/div/div/div[1]/ul/div/div[7]/div/div/a[1]")))
contabilidad.click()


def get_h3_elements(driver, wait_time=10, check_interval=0.5):
    texts_to_find = [
        'Total Movimientos Arrendatario',
        'Total Pagado',
        'Total Descuentos',
        'Total Liquidado Propietario',
        'Total por Liquidar'
    ]

    h3_texts = []
    start_time = time.time()

    for text in texts_to_find:
        while True:
            # Find the element
            h3_element = driver.find_element(
                By.XPATH, f"//p[contains(text(), '{text}')]/following-sibling::h3")

            # Check if the text is no longer the placeholder
            if h3_element.text.strip() != '--':
                h3_texts.append(h3_element.text)
                break
            elif time.time() - start_time > wait_time:
                print(f"Timeout while waiting for text to update for {text}")
                # Or handle the timeout case as you see fit
                h3_texts.append("N/A")
                break

            # Wait for a short interval before checking again
            time.sleep(check_interval)

    return h3_texts


def get_table_data(driver, table_xpath, spinner_xpath):
    try:
        # Wait for the loading spinner to disappear
        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.XPATH, spinner_xpath))
        )

        # Wait for the first row within the tbody of the table to be visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"{table_xpath}/tbody/tr"))
        )

        # Find the table body
        tbody = driver.find_element(By.XPATH, f"{table_xpath}/tbody")

        # Find all rows in the table body
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        # Initialize an empty list to store each row's data
        table_data = []

        # Loop through each row
        for row in rows:
            # Find all cells in the row
            cells = row.find_elements(By.TAG_NAME, "td")

            # Extract the text from each cell and add it to a row list
            row_data = [cell.text for cell in cells]

            # Add the row's data to the table data list
            table_data.append(row_data)
    except:
        table_data = 'None'

    return table_data


def split_text(text):
    # Find the first and last occurrences of '\n'
    first_newline_index = text.find('\n')
    last_newline_index = text.rfind('\n')

    # Split the text into the required parts
    if first_newline_index != -1 and last_newline_index != -1:
        # Part 1: Everything between the first and last '\n', excluding '🏠\n'
        first_part = text[first_newline_index + 1:last_newline_index]
        # Part 2: Everything after the last '\n'
        second_part = text[last_newline_index + 1:]
        # Part 3: Everything before the first comma in the second part
        first_comma_index = second_part.find(',')
        third_part = second_part[:first_comma_index] if first_comma_index != - \
            1 else second_part
    else:
        first_part, second_part, third_part = text, '', ''

    return first_part, second_part, third_part


def generate_month_sequence(start_month: int, start_year: int, end_date: datetime):
    """
    Generates a sequence of months in 'MM-YYYY' format from a starting month and year to a given end date.
    """
    # Ensure start_month is within valid range
    if not 1 <= start_month <= 12:
        raise ValueError("Start month must be between 1 and 12")

    sequence = []
    for year in range(start_year, end_date.year + 1):
        # Determine the starting and ending months for the current year
        start = start_month if year == start_year else 1
        end = end_date.month if year == end_date.year else 12

        # Generate the months for the current year
        for month in range(start, end + 1):
            sequence.append(f'{month:02d}-{year}')

    return sequence


# Example usage
start_month = 6
start_year = 2023
end_date = datetime.now()
dates = generate_month_sequence(start_month, start_year, end_date)
print(dates)

# ver si el modal ya esta presente
prop_name = "Héctor Alejandro  Gutiérrez Rojas"
count = 0

info = {}

file_name = 'output.csv'
list_of_columns = [["Item \ Periodos", "Total Movimientos Arrendatario", "Total Pagado",
                    "Total Descuentos", "Total Liquidado Propietario", "Total por Liquidar"]]

for date in dates:
    # eclick modal
    wait = WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions)
    modal = wait.until(EC.presence_of_element_located((
        By.XPATH, "/html/body/div[1]/div/div[1]/div[2]/div[1]/div/header/div[3]/section")))
    modal.click()
    dialog = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, '.MuiDialog-scrollPaper')))
    wait = WebDriverWait(dialog, 10, ignored_exceptions=ignored_exceptions)
    propietario = wait.until(EC.visibility_of_element_located(
        (By.XPATH, '/html/body/div[3]/div[3]/div/section/div[2]/div[2]/div[1]/div/div/input')))
    if count == 0:
        action.click(propietario).send_keys(prop_name).send_keys(
            Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

    calendario = wait.until(EC.visibility_of_element_located(
        (By.XPATH, '/html/body/div[3]/div[3]/div/section/div[2]/div[2]/div[2]/div/input')))

    if count == 1:
        calendario.send_keys(Keys.CONTROL +
                             "a")
        calendario.send_keys(Keys.DELETE)
        calendario.send_keys(date)
        print(date)
    else:
        calendario.send_keys(date)

    send = driver.find_element(
        By.XPATH, "/html/body/div[3]/div[3]/div/section/div[3]/button")
    send.click()
    # /html/body/div/div/div[1]/div[2]/div[1]/div/section[2]/div[1]/button[1]/span/div
    summary = get_h3_elements(driver)
    table_data = get_table_data(
        driver, "/html/body/div/div/div[1]/div[2]/div[1]/div/section[2]/div[2]/table", "/html/body/div/div/div[1]/div[2]/div[1]/div/section[2]/div[2]/table/tbody/div/div/svg")
    location = table_data[0][0]
    try:
        info[date] = [split_text(location)[2], table_data, summary]
        summary.insert(0, date)
        list_of_columns.append(summary)

    except:
        pass
    count = 1

# First, create or clear the file
open(file_name, 'w').close()

# Now append each list to the file
write_columns_to_csv(file_name, list_of_columns)
# total movimientos arrendatarios /html/body/div/div/div[1]/div[2]/div[1]/div/section[1]/div[1]/div/h3
# total pagado /html/body/div/div/div[1]/div[2]/div[1]/div/section[1]/div[2]/div/h3
# total descuentos /html/body/div/div/div[1]/div[2]/div[1]/div/section[1]/div[3]/div/h3
# total liquidado /html/body/div/div/div[1]/div[2]/div[1]/div/section[1]/div[4]/div/h3
# total por liquidar /html/body/div/div/div[1]/div[2]/div[1]/div/section[1]/div[5]/div/h3
