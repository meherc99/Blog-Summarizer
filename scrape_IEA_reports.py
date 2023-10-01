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
    'website_url': 'https://www.iea.org/',
    'path2chrome_driver': 'chromedriver-mac-arm64/chromedriver',
    'page_index_xpath': '/html/body/div[5]/div/main/div[2]/section/div[2]/div/ul/li',
    'report_section_xpath': "/html/body/div[5]/div/main/div[2]/section/div[1]/ul",
    'filter_tags': {
        'Year': ['2023']
    },
}


def scrape_IEA_reports(final_report_summaries, save_pdf=False):

    """
        Main Function to scrape the IEA website for Analysis reports and save the downloaded file and return the attrubutes table
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
    options.headless = True
    driver = webdriver.Chrome(config['path2chrome_driver'], options=options)
    wait = WebDriverWait(driver, 5)

    for condition_label in config['filter_tags']['Year']:
        try:
            for current_page in np.arange(1, 100):
                attempts = 0
                final_url = config['website_url'] + f'analysis?type=report&year={condition_label}' + f"&page={current_page}"
                driver.get(final_url)
                time.sleep(1)

                while attempts < max_attempts:
                    try:
                        print(f"\n\n --------- Page : {i+1} , Attempt : {attempts + 1}/{max_attempts} tries")
                        ul_element = wait.until(EC.presence_of_element_located((By.XPATH, config['report_section_xpath'])))
                        for report_list_li_tag in ul_element.find_elements(By.TAG_NAME, "li"):
                            if 'report' in report_list_li_tag.text.lower():
                                published_info = report_list_li_tag.text.lower()
                                information_article = {'Title': '', 'Published': '', 'About': '', 'Content': '', 'Scraped_date': -1, 'PDF_url': ''}
                                href = report_list_li_tag.find_element(By.TAG_NAME, "a").get_attribute('href')
                                driver.execute_script("window.open('', '_blank');")
                                driver.switch_to.window(driver.window_handles[1])
                                driver.get(href)

                                time.sleep(3)

                                information_article['Title'] = driver.find_element(By.TAG_NAME, 'title').get_attribute('text')
                                information_article['Published'] = published_info
                                concatenated_text = ''
                                try:
                                    p_elements = driver.find_elements_by_xpath('//*[contains(@class, "m-report-abstract__desc f-rte") or contains(@class, "m-intro-report__desc f-rte")]/p')
                                    for p_element in p_elements:
                                        concatenated_text += p_element.text
                                    information_article['About'] = concatenated_text
                                except:
                                    pass
                                concatenated_urls = ''
                                try:
                                    content_headers = driver.find_elements_by_xpath('//li[@class="m-report-table-contents__item"]/a')
                                    for topic in content_headers:
                                        concatenated_urls = concatenated_urls + ' | ' + str(topic.get_attribute('href'))
                                        information_article['Content'] = concatenated_urls
                                except:
                                    pass
                                information_article['Scraped_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                try:
                                    time.sleep(2)
                                    downlaod_button = driver.find_element_by_xpath("//a[@data-track-eventaction='click download report']")
                                    pdf_url = downlaod_button.get_attribute('href')
                                    information_article['PDF_url'] = pdf_url

                                    if save_pdf:
                                        driver.get(pdf_url)
                                except:
                                    pass

                                final_report_summaries[count] = information_article
                                print(f"\n === {count+1} Article | Extracted Information : {information_article['Title']}")
                                print(information_article)
                                count = count + 1

                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])

                    except:
                        attempts = attempts + 1
        finally:
            driver.quit()

    return final_report_summaries


if __name__ == '__main__':
    final_report_summaries = {}
    final_report_summaries_updated = scrape_IEA_reports(final_report_summaries)
    with open('Data/IEA_final_report_summaries_updated.pkl', 'wb') as f:
        pickle.dump(final_report_summaries_updated, f)

    print("Done.")




