import pandas as pd
import numpy as np
import unidecode
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tqdm import tqdm
import json

#Loading parameters
with open("parameters.json", "r") as file:
    parameters = json.load(file)
    
path_to_chome_driver = parameters["path_to_chome_driver"]

data_dir = parameters["data_dir"]
results_file_name = parameters["results_file_name"]
visible_browser = parameters["visible_browser"]

min_n_char = parameters["min_n_char"]
max_n_char = parameters["max_n_char"]

page_links_df = pd.read_csv(os.path.join(data_dir, results_file_name))



#Launching Chrome driver
options = Options()
options.add_argument('log-level=3')

if visible_browser!="yes":
   options.add_argument('--headless')

driver = webdriver.Chrome(path_to_chome_driver, options=options)


driver.implicitly_wait(1)




#Launching N first words extraction

punc_list = "()"
pattern_punc = "|".join([f"\{punc}" for punc in punc_list])


for i, link in enumerate(tqdm(page_links_df.link.values)):
  
    try:
        driver.get(link)
    except:
        driver.close()
        driver=webdriver.Chrome("C:/Users/hgill/Documents/Perso/Projets/GoogleQA/chromedriver.exe")
        driver.implicitly_wait(2)
        driver.get(link)

    
    title = page_links_df.loc[i, "title"]
    title =  unidecode.unidecode(title) ###removing accents

    title = re.sub(pattern_punc, "", title)
    title = title.lower().split()
   

    paragraphs = [p.text for p in driver.find_elements_by_tag_name("p") if p.text!=""]

    first_para = ""
    title_in = False
    sent = False
    for j,para in enumerate(paragraphs):

        para_norm = unidecode.unidecode(para)
        para_norm = re.sub("\[\[.+\]\]", "", para_norm)

        pattern = "|".join(title)

        if re.search("\.",para_norm):
            sent = True

        if (re.search(pattern, para_norm.lower())):
            title_in = True

        if title_in&sent:
            first_para = para
            content = " ".join(paragraphs[j:])
            break

    page_length = len(content)
    first_para = first_para[:max_n_char] #Limiting to first max_n_char

    page_links_df.loc[i,["first_paragraph", "page_length"]] = first_para , page_length


#Closing the browser
driver.close()
    
    
#Some processing and saving

##Dropping duplicates
page_links_df = page_links_df.drop_duplicates(subset="first_paragraph")

##Filtering out too short paragraphs 
page_links_df["para_length"] = page_links_df.first_paragraph.apply(len)
page_links_df = page_links_df[page_links_df.para_length >= min_n_char] #filtering out too short paragraphs

page_links_df = page_links_df.sort_values(by="page_length",axis=0, ascending=False)  #sorting from articles with longest length to articles with smallest length
page_links_df = page_links_df.reset_index(drop=True) 
page_links_df["article_id"] = range(1,page_links_df.shape[0]+1)  #indexing articles

page_links_df[["article_id", "title", "link", "first_paragraph"]] .to_csv(os.path.join(data_dir, results_file_name), index=None)

print("Everything is fine! :-)")