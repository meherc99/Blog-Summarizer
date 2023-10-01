import pickle
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import numpy as np
import time

config = {
    'website_url': 'https://niti.gov.in/report-and-publication',
    'path2chrome_driver': 'chromedriver-mac-arm64/chromedriver',
    'reports_table_xpath': '/html/body/div[1]/div/div[4]/div/div/div/div/div[1]/div/div/div/div/div/div/div/table/tbody',
    'page_index_xpath': '/html/body/div[1]/div/div[4]/div/div/div/div/div[1]/div/div/div/div/div/div/div/nav/ul/li',
    'filter_tags': {
        'Year': ['2023']
    },
}


def scrape_Niti_Ayog(final_report_summaries, save_pdf=False):

    """
        Main Function to scrape the Niti Ayog website for Analysis reports and save the downloaded file and return the attrubutes table
        All the reports are processed that were published within the range provided in the config section

        :params
            final_report_summaries (dict): empty dictionary that will be updated with all reports attributes
            save_pdf (bool): Boolean to enable or disable saving of downloaded files; default = False
        :return:
            final_report_summaries (dict): Populated dictionary
    """

    count = 0
    max_attempts = 3
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": "Data/",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    # options.headless = True
    driver = webdriver.Chrome(config['path2chrome_driver'], options=options)
    wait = WebDriverWait(driver, 20)
    time.sleep(5)
    for condition_label in config['filter_tags']['Year']:
        row = driver.find_elements_by_xpath(config['reports_table_xpath'])
        index = row.find_elements_by_xpath('/td[1]')[0].text()
        try:
            for page_index in np.arange(0, 25):
                attempts = 0
                final_url = config['website_url'] + f'?page={page_index}'
                driver.get(final_url)
                time.sleep(2)

                while attempts < max_attempts:
                    try:
                        rows = driver.find_elements_by_xpath(config['reports_table_xpath'] + '/tr')
                        for row in rows:
                            index = row.find_elements_by_xpath('/td[1]')[0].text()
                            title = row.find_elements_by_xpath('/td[2]')[0].text()
                            published_info = driver.find_elements_by_xpath(config['reports_table_xpath'] + 'tr/td[3]')[0].text()
                            scraped_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            if condition_label in published_info.lower():
                                information_article = {'Title': title, 'Published': published_info, 'About': '',
                                                       'Content': '', 'Scraped_date': scraped_date, 'PDF_url': ''}
                                try:
                                    pdf_url = driver.find_elements_by_xpath(config['reports_table_xpath'] + 'tr/td[4]')[0]. \
                                        find_element(By.TAG_NAME, "a").get_attribute('href')
                                    information_article['PDF_url'] = pdf_url
                                    if save_pdf:
                                        driver.get(pdf_url)
                                except:
                                    pass
                                final_report_summaries[count] = information_article
                                print(f"\n === {count + 1} Article | Extracted Information : {information_article['Title']}")
                                print(information_article)
                                count = count + 1
                    except:
                        attempts = attempts + 1
        finally:
            driver.quit()

    return final_report_summaries


if __name__ == '__main__':
    final_report_summaries = {}
    final_report_summaries_updated = scrape_Niti_Ayog(final_report_summaries)

    with open('Data/Niti_Ayog_final_report_summaries_updated.pkl', 'wb') as f:
        pickle.dump(final_report_summaries_updated, f)

    print("Done")


