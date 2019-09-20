import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import zipfile


def delete_full_directory(directory):
    # Warning: assumes no subfolders. Designed specifically to delete xml_files folder within the abn_lookup folder
    for file in os.listdir(directory):
        os.remove(directory + '/' + file)
        
    os.rmdir(directory)
    
ASIC_DIR = os.getenv("ASIC_DIR")

download_dir = ASIC_DIR + "/bulk_extract_csvs"

if(os.path.exists(download_dir)):
    delete_full_directory(download_dir)

chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
  "download.default_directory": download_dir,
  "download.prompt_for_download": False,
})

chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
command_result = driver.execute("send_command", params)
    
    
# Navigate driver to download page    
    
driver.get('https://data.gov.au/search?organisation=Australian%20Securities%20and%20Investments%20Commission%20%28ASIC%29&page=2')
driver.find_element_by_link_text('ASIC - Company Dataset').click()
wait_search = WebDriverWait(driver, 10)
element_next = wait_search.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Company Dataset - Current(ZIP)')))
driver.find_element_by_link_text('Company Dataset - Current(ZIP)').click()
wait_search = WebDriverWait(driver, 10)
element_next = wait_search.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Download')))
driver.find_element_by_link_text('Download').click()

soup = BeautifulSoup(driver.page_source, 'html.parser')
file_name = re.search('company_[0-9]+.zip', soup.find_all(attrs = {'class': "url"})[0].get_text()).group(0)
sleep(2)
  
while(os.path.isfile(download_dir + '/' + file_name + ".crdownload")):
    sleep(0.02)
    time = time + 0.02
    if(time >= 600):
        print("Error: file " + file_name + " failed to completely download. Halting. Try again.")
        driver.quit()
    
if(not os.path.isfile(download_dir + '/' + file_name)):
    print("Error: file " + file_name + " did not download at all. Halting. Try again.")

        
driver.quit()


# Finally, unzip the file to get csv, delete the zipped file afterwards

with zipfile.ZipFile(download_dir + '/' + file_name, 'r') as zip_ref:
    zip_ref.extractall(download_dir)
os.remove(download_dir + '/' + file_name)


