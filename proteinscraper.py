import os
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.core.utils import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from requests.exceptions import ConnectionError
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import asyncio
import nest_asyncio

nest_asyncio.apply()

MAX_RETRIES = 5
RETRY_BACKOFF = 2

def fetch_range_html_selenium(driver, uniprot_id):
    url = f"https://www.uniprot.org/uniprotkb/{uniprot_id}/entry"
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'section#ptm_processing protvista-datatable.feature'))
        )
        time.sleep(2)
        html = driver.page_source
        return html
    except Exception as e:
        print(f"Error fetching range HTML for {uniprot_id}: {e}")
        return ""

def fetch_protein_name_selenium(driver, uniprot_id):
    url = f"https://www.uniprot.org/uniprotkb/{uniprot_id}/entry"
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'protvista-datatable.feature'))
        )
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        name_element = soup.select_one('body div#root div.N8ovH div.vJtX6 div.bjUwP.wcdej.entry-page.oVQVq main.wcDnA ul.info-list.info-list--columns li div.decorated-list-item div.decorated-list-item__content strong')
        protein_name = name_element.text.strip() if name_element else 'N/A'
        return protein_name
    except Exception as e:
        print(f"Error fetching protein name for {uniprot_id}: {e}")
        return 'N/A'

def extract_chain_position(html, protein_name):
    soup = BeautifulSoup(html, 'html.parser')
    section = soup.find('section', id='ptm_processing')
    if not section:
        raise Exception("No PTM/Processing section found")

    table = section.find('protvista-datatable', class_='feature')
    if not table:
        raise Exception("No feature table found in PTM/Processing section")

    headers = table.find_all('th')
    description_index = None
    type_index = None
    position_index = None
    for idx, header in enumerate(headers):
        if 'Description' in header.text:
            description_index = idx
        if 'Type' in header.text:
            type_index = idx
        if 'Position(s)' in header.text:
            position_index = idx
        if position_index is not None and type_index is not None and description_index is not None:
            break
    if description_index is None:
        raise Exception("No Description column found in the feature table")
    if type_index is None:
        raise Exception("No Type column found in the feature table")
    if position_index is None:
        raise Exception("No Position column found in the features table")
    rows = table.find_all('tr')
    chains = []

    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 1:
            if 'Chain' in cols[type_index].text:
                start, end = map(str, cols[position_index].text.strip().split('-'))
                description = cols[description_index].text.strip()
                chains.append((start, end, cols[position_index].text.strip(), description))

    if not chains:
        raise Exception("No Chain row found")

    if len(chains) == 1:
        return chains[0][2]

    for chain in chains:
        if protein_name == chain[3]:
            return chain[2]

    raise Exception("No matching Chain row found for the given protein name")

def fetch_features_html_selenium(driver, uniprot_id, range):
    url = f"https://web.expasy.org/cgi-bin/protparam/protparam_bis.cgi?{uniprot_id}@{range}@"
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Grand average of hydropathicity (GRAVY)')]"))
        )
        time.sleep(2)
        html = driver.page_source
        return html
    except Exception as e:
        print(f"Error fetching features HTML for {uniprot_id}: {e}")
        return None

def extract_features(html, range, id):
    data = {}
    name_match = re.search(r'<h3><a.*?>(.*?)<\/a>', html)
    data['Name'] = name_match.group(1) if name_match else 'N/A'
    data['P. sequence'] = range
    data['Protein ID'] = id
    patterns = {
        'pI': r'Theoretical pI:<\/strong>\s*([\d\.]+)',
        'MW': r'Molecular weight:<\/strong>\s*([\d\.]+)',
        'Instability Index': r'The instability index \(II\) is computed to be\s*([\d\.]+)',
        'Aliphatic index': r'Aliphatic index:<\/strong>\s*([\d\.]+)',
        'GRAVY': r'Grand average of hydropathicity \(GRAVY\):<\/strong>\s*(-?[\d\.]+)'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, html)
        data[key] = match.group(1) if match else 'N/A'
    return data

async def scrape_from_id(driver, uniprot_id):
    for attempt in range(MAX_RETRIES):
        try:
            protein_name = fetch_protein_name_selenium(driver, uniprot_id)
            range_html = fetch_range_html_selenium(driver, uniprot_id)
            if not range_html:
                continue
            chain_position = extract_chain_position(range_html, protein_name)
            features_html = fetch_features_html_selenium(driver, uniprot_id, chain_position)
            if not features_html:
                continue
            feature_data = extract_features(features_html, chain_position, uniprot_id)
            return feature_data
        except (ConnectionError, Exception) as e:
            print(f"Error processing {uniprot_id} on attempt {attempt + 1}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_BACKOFF * (2 ** attempt))
            else:
                print(f"Max retries reached for {uniprot_id}. Skipping.")
                return None

async def run_scraping(validate, input_path, output_path, progress, progress_label):
    df = pd.read_excel(input_path)
    results_df = pd.DataFrame(columns=['Name', 'P. sequence', 'Protein ID', 'pI', 'MW', 'Instability Index', 'Aliphatic index', 'GRAVY'])
    uniprot_ids = df['Protein ID'].tolist()
    
    service = ChromeService(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    
    for i, uniprot_id in enumerate(uniprot_ids):
        scraped_data = await scrape_from_id(driver, uniprot_id)
        if scraped_data:
            results_df = pd.concat([results_df, pd.DataFrame([scraped_data])], ignore_index=True)
        progress['value'] = (i + 1) / len(uniprot_ids) * 100
        progress_label.config(text=f"Progress: {i + 1}/{len(uniprot_ids)}")
        progress.update()
    
    driver.quit()
    
    results_df.to_excel(output_path, index=False)
    print("Scraping completed and results saved to", output_path)
    
    # Update the discrepancy writer
    if validate:
        discrepancies = []
        for uniprot_id in uniprot_ids:
            original_data = df[df['Protein ID'] == uniprot_id]
            scraped_data = results_df[results_df['Protein ID'] == uniprot_id]
            if uniprot_id not in results_df['Protein ID'].values:
                empty_row = {
                    'Name': '',
                    'P. sequence': '',
                    'Protein ID': uniprot_id,
                    'pI': '',
                    'MW': '',
                    'Instability Index': '',
                    'Aliphatic index': '',
                    'GRAVY': ''
                }
                results_df = pd.concat([results_df, pd.DataFrame([empty_row])], ignore_index=True)
                continue
            if scraped_data.empty:
                discrepancies.append(f"Protein ID {uniprot_id}: Missing data")
                continue
            for field in ['pI', 'MW', 'Instability Index', 'GRAVY']:
                original_value = str(original_data[field].values[0]).rstrip('0').rstrip('.') if '.' in str(original_data[field].values[0]) else str(original_data[field].values[0])
                scraped_value = str(scraped_data[field].values[0]).rstrip('0').rstrip('.') if '.' in str(scraped_data[field].values[0]) else str(scraped_data[field].values[0])
                if original_value != scraped_value:
                    discrepancies.append(f"Protein ID {uniprot_id}: Field {field} - Original: {original_value}, Scraped: {scraped_value}")
        if discrepancies:
            with open('discrepancies.txt', 'w') as f:
                for discrepancy in discrepancies:
                    f.write(discrepancy + '\n')
            messagebox.showinfo("Validation Complete", f"Validation complete. Discrepancies found and saved to discrepancies.txt")
        else:
            messagebox.showinfo("Validation Complete", "Validation complete. No discrepancies found.")

def start_scraping(validate_var, input_var, output_var, progress, progress_label):
    validate = validate_var.get()
    input_path = input_var.get()
    output_path = output_var.get()
    if not input_path or not output_path:
        messagebox.showerror("Error", "Please provide both input and output file paths.")
        return
    asyncio.run(run_scraping(validate, input_path, output_path, progress, progress_label))

def browse_file(var):
    filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    var.set(filename)

def save_file(var):
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    var.set(filename)

def main():
    root = tk.Tk()
    root.title("Protein Scraper")
    
    tk.Label(root, text="Input File:").grid(row=0, column=0, padx=10, pady=10)
    input_var = tk.StringVar()
    tk.Entry(root, textvariable=input_var, width=50).grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=lambda: browse_file(input_var)).grid(row=0, column=2, padx=10, pady=10)

    tk.Label(root, text="Output File:").grid(row=1, column=0, padx=10, pady=10)
    output_var = tk.StringVar()
    tk.Entry(root, textvariable=output_var, width=50).grid(row=1, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=lambda: save_file(output_var)).grid(row=1, column=2, padx=10, pady=10)
    
    validate_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Validate Data", variable=validate_var).grid(row=2, column=0, columnspan=3, padx=10, pady=10)
    
    progress_label = tk.Label(root, text="Progress: 0/0")
    progress_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
    
    progress = Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
    progress.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
    
    tk.Button(root, text="Run", command=lambda: start_scraping(validate_var, input_var, output_var, progress, progress_label)).grid(row=5, column=0, columnspan=3, padx=10, pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
