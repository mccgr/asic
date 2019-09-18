import re
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy import inspect
import sqlalchemy.types as st
from asxlisting_db import conn_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
        
def go_to_search_page(driver):
    
    try:
        driver.get('https://asic.gov.au/')
        button = driver.find_element_by_link_text("Companies and organisations")
        button.click()
        return(True)
    except:
        return(False)      
        
        
def enter_company_search(driver, company_name):
    
    # Select the dropdown in the right hand corner, and select value "1" for Organisation and Business Names
    select_tag_name = "bnConnectionTemplate:pt_s5:templateSearchTypesListOfValuesId"
    select_icon = driver.find_element_by_name(select_tag_name)
    dropdown = Select(select_icon)
    dropdown.select_by_value("1")
    
    # Now get the text input box immediately below the dropdown, and enter the company name
    company_input_tag_name = 'bnConnectionTemplate:pt_s5:templateSearchInputText'
    company_input_box = driver.find_element_by_name(company_input_tag_name)
    company_input_box.send_keys(company_name)
    
    # Finally, find the "Go" button immediately below and click
    go_button_id = 'bnConnectionTemplate:pt_s5:searchButtonId'
    go_button = driver.find_element_by_id(go_button_id)
    go_button.click()        





def compress_single_lone_characters(name):
    
    split = re.split('(\s|\.)', name)
    
    pieces = []
    
    for bit in split:
      
        if(bit != '.' and bit != ' ' and len(bit) > 0):
          
          pieces.append(bit)
      
    
    fixed_name = ''
    
    for i in range(len(pieces)):
        
        
        if(len(pieces[i]) == 1):
            
            if(i < (len(pieces)-1) and len(pieces[i + 1]) <= 1):
                
                fixed_name = fixed_name + pieces[i]
                
            elif(i < (len(pieces)-1) and len(pieces[i + 1]) > 1):
                
                fixed_name = fixed_name + pieces[i] + ' '
                
            else:
                fixed_name = fixed_name + pieces[i]
                
        else:
            if(i < (len(pieces)-1) and len(pieces[i + 1]) > 0):
                fixed_name = fixed_name + pieces[i] + ' '
                
            else:
                fixed_name = fixed_name + pieces[i]
    
    
    fixed_name = re.sub('\s+', ' ', fixed_name)
    
    
    return(fixed_name)
          
          


def company_name_comparer(company_name_1, company_name_2):
    
    company_name_1 = company_name_1.upper()
    company_name_2 = company_name_2.upper()
    
    # First, strip annoying, troublesome dots, and any annoying spaces on sides. 
    # And get rid of '* ' from the left, so that past company names on ASIC search
    # are treated the same to compared name either way. Also, make sure both upper case
    company_name_1 = company_name_1.replace('* ', '').lstrip(' ').rstrip(' ').replace('\.', '')
    company_name_2 = company_name_2.replace('* ', '').lstrip(' ').rstrip(' ').replace('\.', '')
    
    if(re.search("\(THE\)", company_name_1)):
        company_name_1 = "THE " + re.sub("\(THE\)", "", company_name_1)
        
    if(re.search("\(THE\)", company_name_2)):
        company_name_2 = "THE " + re.sub("\(THE\)", "", company_name_2)
    
    if(company_name_1 == company_name_2):
        return(True)
    
    # next in both names, replace 'LIMITED' with 'LTD', 'PROPRIETARY LIMITED' with 'PTY LTD' and so on
    
    company_name_1 = re.sub('(PROPRIETARY)', 'PTY', re.sub('(LIMITED)', 'LTD', company_name_1))
    company_name_2 = re.sub('(PROPRIETARY)', 'PTY', re.sub('(LIMITED)', 'LTD', company_name_2))
                            
    # Also replace N.L (or N.L.) with just NL
    
    company_name_1 = re.sub('(NOT LIMITED|NON LIMITED|NO LIMITED|NO LIABILITY)', 'NL', company_name_1)
    company_name_2 = re.sub('(NOT LIMITED|NON LIMITED|NO LIMITED|NO LIABILITY)', 'NL', company_name_2)
    
    if(company_name_1 == company_name_2):
        return(True)
    
    # Finally, try AND with &
    company_name_1 = re.sub(' AND ', ' & ', company_name_1)
    company_name_2 = re.sub(' AND ', ' & ', company_name_2)
    
    if(company_name_1 == company_name_2):
        return(True)
        
    else:
        return(False)


def click_first_search_result(driver):
    
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        search_results = soup.find(summary="Organisation and business name search results")
        first_result_tag = search_results.find_all('a')[0]
        first_result_id = first_result_tag.attrs['id']
        first_result = driver.find_element_by_id(first_result_id)
        first_result.click()
    except:
        pass

def get_first_match_tag(soup, company_name):
            
    search_results = soup.find(summary="Organisation and business name search results")
    search_a_tags = search_results.find_all('a')
    names = [re.sub('([\n\r\t]|\s{2,})', ' ', x.get_text()) for x in search_a_tags]
    
    tag = None # Initialized to None, set to a tag if the appropriate tag is found

    for i in range(len(names)):
        if(company_name_comparer(company_name, names[i])):
            tag = search_a_tags[i]
            break
        
    return(tag)

def click_first_search_result_exact_match(driver, company_name):
    
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        search_results = soup.find(summary="Organisation and business name search results")
        search_a_tags = search_results.find_all('a')
        names = [re.sub('([\n\r\t]|\s{2,})', ' ', x.get_text()) for x in search_a_tags]
        
        for i in range(len(names)):
            if(company_name_comparer(company_name, names[i])):
                index = i
                break
                
        first_result_tag = search_a_tags[index]
        first_result_id = first_result_tag.attrs['id']
        first_result = driver.find_element_by_id(first_result_id)
        first_result.click()
    except:
        pass


def click_first_most_relevant_match(driver, company_name):
    
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        
        regex = r"([0-9]+)\s*results found for"
        matches = re.findall(regex, soup.find(title="number of search results").get_text())
        num_total_results = int(matches[0])
        
        num_search_pages = (num_total_results // 10) + 1  # Default number of results per page is 10
        
        for i in range(num_search_pages):
                    
            first_result_tag = get_first_match_tag(soup, company_name)
            
            if(first_result_tag):
                break
                
            else:
                
                if(i < num_search_pages - 1):
                    current_page_button_id = "bnConnectionTemplate:r1:0:pageButton" + str(i + 1)      
                    next_button_id = "bnConnectionTemplate:r1:0:pagingNextButtonTwin"
                    next_button = driver.find_element_by_id(next_button_id)
                    wait_next = WebDriverWait(driver, 10) # Need explicit wait here
                    element_next = wait_search.until(EC.element_to_be_clickable((By.ID, next_button_id)))
                    next_button.click() # click next button for search page results (next ten)
                    wait_search = WebDriverWait(driver, 10) # Need explicit wait here
                    element_search = wait_search.until(EC.element_to_be_clickable((By.ID, current_page_button_id)))
                    soup = BeautifulSoup(driver.page_source, 'html.parser') # Recalculate soup, to account for clicking           
                
        first_result_id = first_result_tag.attrs['id']
        first_result = driver.find_element_by_id(first_result_id)
        first_result.click()
        
    except:
        pass


def is_proper_column(colname):
    if(type(colname) == str):
        if(len(colname)):
            return(True)
        else:
            return(False)
    else:
        return(False)
        
        
        
def get_company_info_table(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    info_table = soup.find(attrs = {'class': 'detailTable'})
    
    colnames = pd.read_html(str(info_table))[0][0]
    values = pd.read_html(str(info_table))[0][1]

    nonnull_col_slice = [is_proper_column(x) for x in colnames]
    colnames = colnames[nonnull_col_slice]

    colnames = colnames.map(lambda x: re.sub("[:\(\)]", "", x.rstrip(" ").replace(" ", "_").lower())).tolist()
    values = values[nonnull_col_slice].tolist()

    df = pd.DataFrame([values], columns = colnames)
    df = df.rename(columns = {'name': 'company_name_asic'})
    
    if('abn' in df.columns):
        df['abn'] = df['abn'].map(lambda x: x.rstrip('(External Link)').rstrip(' '))
        
    if('former_names' in df.columns):
        if(df['former_names'] is not None):
            df['former_names'] = df['former_names'].map(lambda x: x.split(', '))
        else:
            df['former_names'] = None
            
    
    return(df)


def in_former_names(company_name, df):
    if('former_names' in df.columns):
        if(df.loc[0, 'former_names'] is not None):
            for name in df.loc[0, 'former_names']:
                if(company_name_comparer(company_name, name)):
                    return(True)
    return(False)


def search_results_and_extract_info(driver, company_name):
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    search_results = soup.find(summary="Organisation and business name search results")
    search_a_tags = search_results.find_all('a')
    names = [re.sub('([\n\r\t]|\s{2,})', ' ', x.get_text()) for x in search_a_tags]
    
    # First, check the names that appear on the search page. If there is a good match, click
    for i in range(len(names)):
        if(company_name_comparer(company_name, names[i])):
            correct_tag = search_a_tags[i]
            correct_tag_id = correct_tag.attrs['id']
            driver.find_element_by_id(correct_tag_id).click()
            wait_page = WebDriverWait(driver, 10)
            element_page = wait_page.until(EC.presence_of_element_located((By.CLASS_NAME, 'detailTable')))
            df = get_company_info_table(driver)
            return(df)
    
    for tag in search_a_tags:
        tag_id = tag.attrs['id']
        driver.find_element_by_id(tag_id).click()
        wait_page = WebDriverWait(driver, 10)
        element_page = wait_page.until(EC.presence_of_element_located((By.CLASS_NAME, 'detailTable')))
        df = get_company_info_table(driver)
        
        in_hist = in_former_names(company_name, df)
        
        if(company_name_comparer(company_name, df.loc[0, 'company_name_asic']) or in_hist):
            
            return(df)
            
        else:
            use_asic_back_button(driver)
            wait_page = WebDriverWait(driver, 10)
            element_page = wait_page.until(EC.presence_of_element_located((By.XPATH, '//table[@summary = "Organisation and business name search results"]')))
    
    # If nothing acceptable found after the above two searches, return None
    return(None)


def get_most_relevant_match_df(driver, company_name):
    
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        
        regex = r"([0-9]+)\s*results found for"
        matches = re.findall(regex, soup.find(title="number of search results").get_text())
        num_total_results = int(matches[0])
        
        num_search_pages = (num_total_results // 10) + 1  # Default number of results per page is 10
        
        for i in range(num_search_pages):
                    
            first_result_df = search_results_and_extract_info(driver, company_name)
            
            if(first_result_df is not None):
                return(first_result_df)
                
            else:
                
                if(i < num_search_pages - 1):
                    current_page_button_id = "bnConnectionTemplate:r1:0:pageButton" + str(i + 1)      
                    next_button_id = "bnConnectionTemplate:r1:0:pagingNextButtonTwin"
                    next_button = driver.find_element_by_id(next_button_id)
                    wait_next = WebDriverWait(driver, 10) # Need explicit wait here
                    element_next = wait_search.until(EC.element_to_be_clickable((By.ID, next_button_id)))
                    next_button.click() # click next button for search page results (next ten)
                    wait_search = WebDriverWait(driver, 10) # Need explicit wait here
                    element_search = wait_search.until(EC.element_to_be_clickable((By.ID, current_page_button_id)))
                    soup = BeautifulSoup(driver.page_source, 'html.parser') # Recalculate soup, to account for clicking           
                
        # If nothing found after clicking each page, return None
        return(None)
        
        
    except:
        return(None)


def extract_asic_details(driver, linked_id, company_name):
    
    try:
        if(driver.current_url == 'data:,'):
            go_to_search_page(driver)
            
        name = re.sub('^(NSX|SIM) - ', '', company_name) # If SIM or NSX, extract the formal company name

        url = driver.current_url 
        # the url before we do the search and press go. If reCaptcha not already done, reCaptcha appears before going to search page
        enter_company_search(driver, name)

        wait_search = WebDriverWait(driver, 600) # Wait up to 10 minutes, as we deal with reCaptcha manually
        element_search = wait_search.until(EC.url_changes(url))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        straight_to_result = len(soup.find_all(attrs = {'class': 'detailTable'}))
        
        if(straight_to_result):
            # If this is the case, the search has resulted in a direct straight to the result page, not a search. 
            # Hence, just get the table. If the name matches, keep raw_df
            raw_df = get_company_info_table(driver)
            name_match = company_name_comparer(name, raw_df.loc[0, 'company_name_asic'])
            hist_match = in_former_names(name, raw_df)
            if(not (name_match or hist_match)):
                raw_df = None
                
        elif(re.search("0 results found for", soup.get_text())):
            df = pd.DataFrame({'linked_id': [linked_id], 'company_name': [company_name], \
                               'company_name_asic': [None]})
            return(df)
        
            
        else:
            # Else, go through the search results
            raw_df = get_most_relevant_match_df(driver, name)
        
        df = pd.DataFrame({'linked_id': [linked_id], 'company_name': [company_name]})
        df = pd.concat([df, raw_df], axis = 1)
        
        for col in df.columns:
            
            if(re.search('(^date_|_date$|_date_)', col) is not None):
                df[col] = pd.to_datetime(df[col], format = "%d/%m/%Y")
    
        return(df)
    
    except:
        return(None)




def write_asic_details(driver, engine, linked_id, company_name):
    
    try:
        df = extract_asic_details(driver, linked_id, company_name)

        inspector = inspect(engine)

        types = {'linked_id': st.Integer(),
                 'company_name': st.Text()}

        table_exists = 'asx' in inspector.get_table_names(schema="asic")

        current_cols_sql = """SELECT column_name FROM information_schema.columns 
                            WHERE table_schema = 'asic' AND table_name = 'asx'
                            """

        current_cols = pd.read_sql(current_cols_sql, engine)['column_name'].tolist()

        for col in df.columns:

            if(re.search('(^date_|_date$|_date_)', col)):
                types[col] = st.Date()

                if(col not in current_cols and table_exists):

                    new_col_sql = "ALTER TABLE asic.asx ADD COLUMN " + col + " DATE"
                    engine.execute(new_col_sql)

            elif(col == 'former_names'):

                types[col] = st.ARRAY(st.Text(), dimensions = 1)

                if(col not in current_cols and table_exists):

                    new_col_sql = "ALTER TABLE asic.asx ADD COLUMN " + col + " TEXT[]"
                    engine.execute(new_col_sql)

            else:
                types[col] = st.Text()

                if(col not in current_cols and table_exists):

                    new_col_sql = "ALTER TABLE asic.asx ADD COLUMN " + col + " TEXT"
                    engine.execute(new_col_sql)



        df.to_sql('asx', engine, schema="asic", if_exists="append", 
            index=False, dtype = types)

        return(True)
    
    except:
        return(False)




def use_asic_back_button(driver):
    # This function uses the internal back button on ASIC's API (which is the back button we want to use), 
    # NOT the browser back button
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        back_button_tag = soup.find(attrs = {"class": re.compile("buttonBack")})
        back_button_id = back_button_tag.attrs['id']
        back_button = driver.find_element_by_id(back_button_id)
        back_button.click()
    except:
        pass


def split_former_names(former_names_string):
    if(type(former_names_string) == str):
        return(former_names_string.split(', '))
    else:
        return(None)



def get_companies_to_process_df(engine):
    
    # This function gets a dataframe which contains the linked_id, current issuer_id, and current company_name of entities
    # which have not been processed into asic.asx
    
    inspector = inspect(engine)
    table_exists = 'asx' in inspector.get_table_names(schema="asic")

    if(table_exists):
        
        sql = """
          WITH max_ids AS (SELECT MAX(issuer_id) AS issuer_id, linked_id 
          FROM asxlisting.issuer_id_link GROUP BY linked_id)
          SELECT a.issuer_id, max_ids.linked_id, a.company_name FROM asxlisting.issuer_ids AS a
          INNER JOIN max_ids
          USING (issuer_id)
          LEFT JOIN asic.asx AS b
          USING(linked_id)
          WHERE b.linked_id IS NULL
          ORDER BY linked_id
          """      
          
    else:
        
        sql = """
         WITH max_ids AS (SELECT MAX(issuer_id) AS issuer_id, linked_id 
         FROM asxlisting.issuer_id_link GROUP BY linked_id)
         SELECT issuer_id, linked_id, company_name FROM asxlisting.issuer_ids
         INNER JOIN max_ids
         USING (issuer_id)
         ORDER BY linked_id
      """

    
    df = pd.read_sql(sql, engine)
    return(df)









types = {'linked_id': st.Integer(),
         'company_name': st.Text(),
         'company_name_asic': st.Text(),
         'acn': st.Text(),
         'abn': st.Text(),
         'previous_state_number': st.Text(),
         'previous_state_of_registration': st.Text(),
         'registration_date': st.Date(),
         'next_review_date': st.Date(),
         'status': st.Text(),
         'type': st.Text(),
         'locality_of_registered_office': st.Text(),
         'regulator': st.Text(),
         'former_names': st.ARRAY(st.Text(), dimensions = 1),
         'date_deregistered': st.Date(),
         'arbn': st.Text()
         }

asic_information.to_sql('asx', engine, schema="asic", if_exists="replace", 
            index=False, dtype = types)
            
            
            


