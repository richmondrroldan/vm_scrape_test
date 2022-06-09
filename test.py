#from scrapers.db import add_job
from selenium import webdriver
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
from decouple import config
import time
from selenium.common.exceptions import NoSuchElementException
from utils.userAgent import switchUserAgent
from utils.stripNewLine import stripNewLine
from sqlalchemy import create_engine
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


def indeed_rss(driver, s3_upload=False):
    SCRAPE_TIME = datetime.now().strftime(r"%Y-%m-%d-%H-%M")
    fname = f"ph_{SCRAPE_TIME}_indeedrss.csv"

    jobList = []
    companyList = []
    pubDateList = []
    geoList = []
    JobDescriptions = []
    linkList = []
    locationList = []
    guidList = []
    fullJobDescription = []
    r = requests.get(f'https://ph.indeed.com/rss/jobs?q=engineer&sort=date')
    soup = bs(r.content, features='xml')

    jobs = soup.findAll('item')

    for job in jobs:
        jobTitle = job.find('title').text
        companies = job.find('source').text
        pubDate = job.find('pubDate').text
        geoLoc = job.find('georss:point').text
        jd = job.find('description').text
        links = job.find('link').text
        guid = job.find('guid').text
        city = jobTitle.split('-')[-1].strip()

        jobList.append(jobTitle)
        companyList.append(companies)
        pubDateList.append(pubDate)
        geoList.append(geoLoc)
        JobDescriptions.append(jd)
        linkList.append(links)
        locationList.append(city)
        guidList.append(guid)
    
    # for link in linkList:
    #     # switchUserAgent(driver)
    #     driver.get(link)
    #     time.sleep(5)
    #     try:
    #         driver.find_element_by_xpath(
    #             '//*[@id="popover-x"]').click()
    #     except NoSuchElementException:
    #         pass
    #     time.sleep(5)

    #     try:
    #         jobDesc = driver.find_element_by_xpath(
    #             '//*[@id="vjs-desc"]')
    #         fullJobDescription.append(jobDesc.text)
    #         continue
    #     except NoSuchElementException:
    #         pass

    #     try:
    #         jobDesc = driver.find_element_by_xpath(
    #             '//*[@id="jobDescriptionText"]')
    #         fullJobDescription.append(jobDesc.text)
    #         driver.back()
    #     except:
    #         continue



    data = list(zip(guidList, jobList, companyList, pubDateList, geoList, locationList,
                    JobDescriptions, fullJobDescription, linkList))
    #data = [jobList, companyList, pubDateList, locationList, JobDescriptions, linkList]
    df = pd.DataFrame(data, columns=[
        "JobID", "JobTitle", "Company", "PublicationDate",
        "GeoRSS", "Location", "rssJobDescription", 
        "fullJobDescription", "Link"
    ])

    df = df.replace(r"\n", " ", regex=True)
    
    return df
    #add_job(df)
    
    df.to_csv(fname)

indeed_rss(driver)
