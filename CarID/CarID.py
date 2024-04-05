from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime

# Set up Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

def reset_to_start():   
    # Run the main function
    print("\n*********Resetting to start*********\n")
    driver.get('https://www.carid.com/')
    # Click the search icon
    search_icon_xpath = '/html/body/div[4]/div/header/div[1]/div/div[2]/div'
    driver.find_element(By.XPATH, search_icon_xpath).click()
    time.sleep(5)  # wait for the search box to activate

# Function to read the input file
def read_input_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

# Function to perform the search on the website
def search_sku(sku):
    search_field_xpath = '/html/body/div[8]/div[2]/div/div[1]/div/div/form/div[2]/div/input'
    results_list_xpath = '/html/body/div[8]/div[2]/div/div[1]/div/div/form/div[3]/div/div/ul'
    
    # Enter SKU and press ENTER
    search_input = driver.find_element(By.XPATH, search_field_xpath)
    search_input.clear()
    time.sleep(1)
    search_input.send_keys(sku)
    time.sleep(5)
    
    # Collect search results
    results = driver.find_elements(By.XPATH, f"{results_list_xpath}/li")
    # instead of [result.text for result in results]we return the first result
    return results[1].text if results else "No results found"

# Main function
datadict = {}
def main(input_file, output_folder):
    skus = read_input_file(input_file)
    results = {}
    tracker = 0
    for sku in skus:
        tracker += 1
        if tracker % 25 == 0:
            reset_to_start()
        print(f"\nProcessing SKU {tracker}/{len(skus)}: {sku}")
        try:
            # we split SKu by space and get the last element
            extracted_sku = sku.split()[-1]
            results[sku] = search_sku(sku)
            productinfo = results[sku].split("\n")
            brand = productinfo[0].split("®")[0].strip()
            product = productinfo[0].split("®")[1].strip()
            if extracted_sku not in product:
                print(f"-------------------SKU mismatch: {extracted_sku} != {product}-------------------")
                #we throw an error so we can catch it and continue
                raise Exception('SKU mismatch')
            stock = productinfo[1].split("$")[0].strip()
            if not stock or stock == '':
                stock = 'In Stock'
            price = productinfo[1].split("$")[1].strip()
            if 'Save' in price:
                price = productinfo[1].split("$")[2].strip()
            if 'mpn' in price:
                price = price.split('mpn')[0].strip()
            dataload = {'SKU': sku, 'Brand': brand, 'Product': product, 'Stock': stock, 'Price': price}
            datadict[sku] = dataload
            print(dataload)
            #save to a file just in case
            with open(f'{output_folder}outputBACKUP.txt', 'a') as file:
                file.write(f'{dataload}\n')
        except:
            print(f"-------------------Error processing SKU: {sku}-------------------")
            datadict[sku] = {'SKU': sku, 'Brand': 'Error', 'Product': 'Error', 'Stock': 'Error', 'Price': 'Error'}
            with open(f'{output_folder}outputBACKUP.txt', 'a') as file:
                file.write(f'Error processing SKU: {sku}\n')
    driver.quit()

# Specify the paths to your input and output directory
input_file_path = 'C:/Users/ryexd/Documents/GitHub/WebScraping/CarID/input/input.txt'
output_folder_path = 'C:/Users/ryexd/Documents/GitHub/WebScraping/CarID/output/'

reset_to_start()

main(input_file_path, output_folder_path)

# Write the output to a excel file
import pandas as pd
# Convert datadict values to a list of dictionaries
data_list = list(datadict.values())

# Create DataFrame from the list of dictionaries
df = pd.DataFrame(data_list)

# Write the DataFrame to an Excel file
output_file = f'{output_folder_path}output_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
df.to_excel(output_file, index=False)