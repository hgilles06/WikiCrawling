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

page_paragraph_limit = parameters["page_paragraph_limit"]

page_links_df = pd.read_csv(os.path.join(data_dir, results_file_name))

output_files = []



#Launching Chrome driver
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('log-level=3')

if visible_browser!="yes":
   options.add_argument('--headless')

driver = webdriver.Chrome(path_to_chome_driver, options=options)


driver.implicitly_wait(1)




#Launching N first characters extraction

punc_list = "()"
pattern_punc = "|".join([f"\{punc}" for punc in punc_list])


for i, link in enumerate(tqdm(page_links_df.link.values)):

    try:
        driver.get(link)
    except:
        driver.close()
        driver=webdriver.Chrome(path_to_chome_driver, options=options)
        driver.implicitly_wait(1)
        driver.get(link)


    title = page_links_df.loc[i, "title"]
    title =  unidecode.unidecode(title) ###removing accents

    title = re.sub(pattern_punc, "", title)
    title = title.lower().split()


    paragraphs = [p.text for p in driver.find_elements_by_tag_name("p") if p.text!=""]

    first_para = ""
    title_in = False
    sent = False
    content = []
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
            content.append(first_para)
            break

    counter = page_paragraph_limit
    if len(paragraphs) > 0:

        selected_para = ""
        selected_para_len = 0

        for para in paragraphs:
            selected_para_len = selected_para_len if len(para) < selected_para_len else len(para)
            selected_para = selected_para if len(para) < selected_para_len else para
            counter -= 1

            if counter < 0:
                break

        page_links_df.loc[i, ["paragraph", "page_length"]] = selected_para[:max_n_char], selected_para_len

        output_files.append(page_links_df.loc[i])


#Closing the browser
driver.close()

#Some processing and saving
output_df = pd.DataFrame(output_files, columns = ['title', 'link', 'paragraph', 'page_length'])

##Dropping duplicates
page_links_df = page_links_df.drop_duplicates(subset="paragraph")

output_df = output_df.drop_duplicates(subset="paragraph")

##Filtering out too short paragraphs
output_df["para_length"] = page_links_df.paragraph.apply(str.strip).apply(len)
output_df = output_df[output_df.para_length >= min_n_char] #filtering out too short paragraphs

output_df = output_df.sort_values(by="page_length",axis=0, ascending=False)  #sorting from articles with longest length to articles with smallest length
output_df = output_df.reset_index(drop=True)
output_df["article_id"] = range(1,output_df.shape[0]+1)  #indexing articles

#TODO changed the filename for the outout file, might want to do the same for the output file.
output_df[["article_id", "title", "link", "paragraph"]] .to_csv(os.path.join(data_dir, "WikiPagePromptsV2.csv"), index=None)

print("Everything is fine! :-)")
