from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
import pymysql
import time
import json
import os
import re
import math
import pandas as pd

create_date = str(datetime.now()).split(' ')[0].strip()

mydb = pymysql.connect(host="183.111.103.165",
                        user="vision",
                        passwd="vision9551",
                        db="kisti_crawl_test",
                        charset='utf8')
cursor = mydb.cursor()

from sqlalchemy import create_engine
db_connection_str = 'mysql+pymysql://vision:vision9551@183.111.103.165/kisti_crawl_test'
db_connection = create_engine(db_connection_str)
conn = db_connection.connect()


def insert_db(product_info,product_spectable,review_keyword):
    product_info_list = list()
    product_info["CREATE_DATE"] = create_date
    product_info_list.append(product_info)
    product_info_df = pd.DataFrame(product_info_list)
    product_info_df.to_sql(name='tb_dnw_product_info',con=db_connection, if_exists='append', index=False)

    index_1 = 1
    product_spectable_list = list()
    for key in product_spectable:
        if key != '':
            product_spectable_dict = dict()
            product_spectable_dict["PCATEGORY"] = product_info["PCATEGORY"]
            product_spectable_dict["PCODE"] = product_info["PCODE"]
            product_spectable_dict["PRODUCT_IDX"] = index_1
            product_spectable_dict["CREATE_DATE"] = create_date
            product_spectable_dict["TITLE"] = key
            product_spectable_dict["CONTENT"] = product_spectable[key]
            product_spectable_list.append(product_spectable_dict)
            index_1 += 1
    product_spectable_df= pd.DataFrame(product_spectable_list)
    product_spectable_df.to_sql(name='tb_dnw_product_detail',con=db_connection, if_exists='append', index=False)

    index_2 = 1
    review_keyword_list = list()
    for key in review_keyword:
        review_keyword_dict = dict()
        review_keyword_dict["PCATEGORY"] = product_info["PCATEGORY"]
        review_keyword_dict["PCODE"] = product_info["PCODE"]
        review_keyword_dict["PRODUCT_IDX"] = index_2
        review_keyword_dict["CREATE_DATE"] = create_date
        review_keyword_dict["KEYWORD"] = review_keyword[key]
        review_keyword_list.append(review_keyword_dict)
        index_2 += 1
    review_keyword_df= pd.DataFrame(review_keyword_list)
    review_keyword_df.to_sql(name='tb_dnw_review_keyword',con=db_connection, if_exists='append', index=False)

def insert_review_db(review):
    index_3 = 1
    review_list = list()
    for i in range(len(review)):
        review_dict = dict()
        review_dict["PCATEGORY"] = review[i]["PCATEGORY"]
        review_dict["PCODE"] = review[i]["PCODE"]
        review_dict["PRODUCT_IDX"] = index_3
        review_dict["CREATE_DATE"] = create_date
        review_dict["RATING"] = math.floor(int(re.sub('[가-힣]','',review[i]["Rating"]))/20)
        review_dict["DATE"] = review[i]["Date"]
        review_dict["MALL"] = review[i]["Mall"]
        review_dict["TITLE"] = review[i]["Title"]
        review_dict["CONTENT"] = review[i]["Text"]
        index_3 += 1
        review_list.append(review_dict)
    review_df= pd.DataFrame(review_list)
    review_df.to_sql(name='tb_dnw_review',con=db_connection, if_exists='append', index=False)


# EachStarPercent
def getEachStarPercent(product_info, soup):
    for star_index in [5,4,3,2,1]:
        starPercent_html = soup.select_one(f"a#danawa-prodBlog-companyReview-score-{star_index} span.percent")
        starPercent_str = starPercent_html.get_text().strip().rstrip("%")
        product_info[f"{star_index}STAR"] = int(starPercent_str)

# ReviewKeyword
def getReviewKeyword(review_keyword, soup):
    reviewKeyword_list = soup.select_one("ul.tag_list").select("li")[1:]
    index = 1
    for reviewKeyword in reviewKeyword_list:    
        review_keyword[f"ReviewKeyword_{index}"] = reviewKeyword.get_text().strip()
        index += 1

def getRivewList(pcategory, pcode, review_page, review_count, review):
    review_count = getReviewText(pcategory, pcode,review_count, review)
    while True:
        if review_count > REVIEW_COUNT:
            break
        try:
            review_page += 1
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            review_page_html = soup.select_one(f"a[data-pagenumber = '{review_page}']")
            if review_page_html == None:
                break

            driver.find_element(By.CSS_SELECTOR,f"a[data-pagenumber = '{review_page}']").click()
            review_count = getReviewText(pcategory,pcode,review_count,review)
        except:
            break
    return review_count

def getReviewText(pcategory,pcode,review_count, review):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    reviewer_list = soup.select("li.danawa-prodBlog-companyReview-clazz-more")
    for reviewer in reviewer_list:
        if review_count > REVIEW_COUNT:
            break
        reviewDict = dict()
        Rating = reviewer.select_one("div.top_info span.star_mask").get_text().strip()
        Date = reviewer.select_one("div.top_info span.date").get_text().strip()
        Mall = reviewer.select_one("div.top_info span.mall").get_text().strip()
        Title = reviewer.select_one("div.rvw_atc p.tit").get_text().strip()
        Text = reviewer.select_one("div.rvw_atc div.atc").get_text().strip()
        reviewDict["PCATEGORY"] = pcategory
        reviewDict["REVIEW_NUMBER"] = review_count
        reviewDict["PCODE"] = pcode
        reviewDict["Rating"] = Rating
        reviewDict["Date"] = Date
        reviewDict["Mall"] = Mall
        reviewDict["Title"] = Title
        reviewDict["Text"] = Text
        review.append(reviewDict)
        review_count += 1
    return review_count

# SpecTable
def getSpecTable(product_spectable, soup):
    specTable_key = soup.select("table.spec_tbl tbody tr th.tit")
    specTable_value = soup.select("table.spec_tbl tbody tr td.dsc")
    specTable_key_list = list()
    specTable_value_list = list()
    for list_index in specTable_key:
        specTable_key_list.append(list_index.get_text().strip())
    for list_index in specTable_value:
        specTable_value_list.append(list_index.get_text().strip().replace("\n","").replace("\t","").rstrip("(제조사 웹사이트 바로가기)"))
    for list_index in range(len(specTable_key_list)):
        product_spectable[specTable_key_list[list_index]] = specTable_value_list[list_index]

# 상품 정보페이지로 넘어가는 함수
def goToDetailPage(detailURL,review_count,product_index):
    
    product_info = dict()
    product_spectable = dict()
    review_keyword = dict()
    # Selenium
    driver.get(detailURL)
    page_source = driver.page_source
    # BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    script_str = soup.find("script", type="application/ld+json")
    try:
        script_json = json.loads(script_str.get_text())
    except:
        pass
    try:       
        # Product Key
        pcode = script_json["sku"]
        product_info["PCODE"] = pcode
        product_info["PCATEGORY"] = pcategory
    except:
        pass
    # try:
    #     # productURL
    #     product_info["URL"] = script_json["offers"]["url"]
    # except:
    #     pass
    try:
        product_info["PRODUCT_IDX"] = product_index
    except:
        pass
    try:
        # Name
        product_info["PRODUCT_NAME"] = script_json["name"]
    except:
        pass
    try:
        # Price
        product_info["PRODUCT_PRICE"] = script_json["offers"]["lowPrice"]
    except:
        pass
    # try:    
    #     # PriceCurrency
    #     product_info["PriceCurrency"] = script_json["offers"]["priceCurrency"]
    # except:
    #     pass
    try:
        # launch date
        product_info["LAUNCH_DATE"] = soup.select_one("div.made_info").select_one("span").get_text().strip().split(":")[1].strip()
    except:
        pass
    try:
        # Brand
        product_info["BRAND_NAME"] = script_json["brand"]["name"]
    except:
        pass
    # try:
    #     # imageURL
    #     product_info["ImageURL"] = script_json["image"][0]
    # except:
    #     pass
    # try:
    #     # description
    #     product_info["Description"] = script_json["description"]
    # except:
    #     pass
    try:
        # RatingStar
        product_info["REVIEW_SCORE"] = float(script_json["aggregateRating"]["ratingValue"])
    except:
        pass
    try:
        # ReviewCount
        product_info["REVIEW_NUMBER"] = int(script_json["aggregateRating"]["reviewCount"])
    except:
        pass
    try:
        # EachStarPercent
        getEachStarPercent(product_info, soup)
    except:
        pass
    try:
        # ReviewKeyword
        getReviewKeyword(review_keyword, soup)
    except:
        pass
    try:
        # SpecTable
        getSpecTable(product_spectable, soup)
    except:
        pass
    try:
        # ReviewText
        review_page = 1
        if review_count < REVIEW_COUNT:
            review_count = getRivewList(pcategory, pcode, review_page, review_count, review)
    except:
        pass
    
    try:
        insert_db(product_info,product_spectable,review_keyword)
    except:
        pass
    return review_count

# 다음 페이지로 넘기는 함수
def goToNextPage(cur_page,soup):
    page_html = soup.select("div.number_wrap a")
    for index in page_html:
        isNextPage = int(index.get_text())
        if isNextPage > cur_page:
            cur_page = isNextPage
            driver.get(URL_ADDRESS + URL_PREFIX + pcategory)
            driver.execute_script(f"movePage({cur_page})")
            driver.implicitly_wait(300)
            time.sleep(5)
            return cur_page
        else:
            continue

options = Options()
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(300)

URL_ADDRESS = "https://prod.danawa.com/"
URL_PREFIX = "list/?cate="
CONTENT_COUNT = 300
REVIEW_COUNT = 20000
input_txt = open("./input.txt","r", encoding="utf-8")
TITLE_LIST = input_txt.read().splitlines()

for pcategory in TITLE_LIST:
    content_count = 1
    review_count = 1
    cur_page = 1
    product_index = 1
    isdone = False
    review = list()

    driver.get(URL_ADDRESS + URL_PREFIX + pcategory)

    driver.implicitly_wait(300)
    time.sleep(1)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    list_html = soup.select_one("li[data-view-method='LIST'] a")
    driver.find_element(By.CSS_SELECTOR,"li[data-view-method='LIST'] a").click()
    driver.implicitly_wait(300)
    time.sleep(5)

    while(True):
        # try:
            # Selenium && BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        # 상품을 list로 저장
        contents = soup.select("a[name='productName']")
        # 상품의 URL을 따서 goToDetailPage함수 실행
        for content in contents:
            if content_count <= CONTENT_COUNT:
                detailURL = content.attrs["href"]
                review_count = goToDetailPage(detailURL,review_count,product_index)
                product_index += 1
                content_count += 1
            else:
                isdone = True
                break
        if isdone == True:
            insert_review_db(review)
            break

        # 페이지 넘기는 함수
        cur_page = goToNextPage(cur_page, soup)
        if cur_page == None:
            insert_review_db(review)
            break
        # except:
        #     with open('error.txt','a') as f:
        #         f.write(pcategory)
        #         f.write("\n")