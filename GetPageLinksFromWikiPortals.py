from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import os
import pandas as pd

from tqdm import tqdm
import json


def get_page_links(driver, portal_link):
    driver.get(portal_link)
    sections = driver.find_elements_by_class_name("mw-body-content")
    df = pd.DataFrame(columns=["title", "link"])

    line = 0
    for section in sections:
        section_info = [(elm.text, elm.get_attribute("href")) for elm in section.find_elements_by_tag_name("a")]
        section_info = pd.DataFrame(section_info, columns=["title", "link"])
        df = df.append(section_info)
    return df


# Loading parameters
with open("parameters.json", "r") as file:
    parameters = json.load(file)

path_to_chome_driver = parameters["path_to_chome_driver"]

data_dir = parameters["data_dir"]
results_file_name = parameters["results_file_name"]
visible_browser = parameters["visible_browser"]
wiki_portal_links = parameters["wiki_portal_links"]

# Loding Wiki portal links
portal_links_list = pd.read_csv(wiki_portal_links, sep="\n", header=None).iloc[:, 0]

# Launching Chrome driver
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('log-level=3')

if visible_browser != "yes":
    options.add_argument('--headless')

driver = webdriver.Chrome(path_to_chome_driver, options=options)

driver.implicitly_wait(1)

# Link Extraction
for i, link in enumerate(tqdm(portal_links_list)):

    if i == 0:
        page_links_df = get_page_links(driver, link)
        continue

    page_links_df = page_links_df.append(get_page_links(driver, link))

# Closing Chrome driver
driver.close()

# Saving

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

page_links_df = page_links_df.drop_duplicates()
page_links_df.to_csv(os.path.join(data_dir, results_file_name), index=None)

print("Everything is fine! :-)")


