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
from tqdm import tqdm

create_date = str(datetime.now()).split(' ')[0].strip()

mydb = pymysql.connect(host="183.111.103.165",
                        user="vision",
                        passwd="vision9551",
                        db="kisti_crawl_test",
                        charset='utf8')
cursor = mydb.cursor()

def checkDictValue_str(dict,key):
    value = dict.get(key)
    if value == None:
        return "null"
    else:
        return dict[key].replace('"','`').replace("'","`")

def checkDictValue_int(dict,key):
    value = dict.get(key)
    if value == None:
        return 0
    else:
        return dict[key]

def insert_db(product_info,product_spectable,review_keyword):
    product_info_dict = dict()
    product_info_dict["pcategory"] = checkDictValue_str(product_info,"pcategory")
    product_info_dict["pcode"] = checkDictValue_str(product_info,"Product_key")
    product_info_dict["product_idx"] = int(product_info["order"])
    product_info_dict["create_date"] = create_date
    product_info_dict["level1"] = checkDictValue_str(product_info,"Level_1")
    product_info_dict["level2"] = checkDictValue_str(product_info,"Level_2")
    product_info_dict["level3"] = checkDictValue_str(product_info,"Level_3")
    product_info_dict["level4"] = checkDictValue_str(product_info,"Level_4")
    product_info_dict["product_name"] = checkDictValue_str(product_info,"Name")
    product_info_dict["product_price"] = checkDictValue_int(product_info,"Price")
    product_info_dict["launch_date"] = checkDictValue_str(product_info,"LaunchDate")
    product_info_dict["brand_name"] = checkDictValue_str(product_info,"BrandName")
    product_info_dict["review_score"] = checkDictValue_int(product_info,"ProductRatingStar")
    product_info_dict["review_number"] = checkDictValue_int(product_info,"ReviewCount")
    product_info_dict["5star"] = checkDictValue_int(product_info,"5star")
    product_info_dict["4star"] = checkDictValue_int(product_info,"4star")
    product_info_dict["3star"] = checkDictValue_int(product_info,"3star")
    product_info_dict["2star"] = checkDictValue_int(product_info,"2star")
    product_info_dict["1star"] = checkDictValue_int(product_info,"1star")
    # print(product_info_dict)
    cursor.execute(f"""INSERT INTO `TB_DNW_PRODUCT_INFO` (pcategory,pcode,product_idx,create_date,product_name,product_price,launch_date,brand_name,review_score,review_number,5star,4star,3star,2star,1star) VALUES("{product_info_dict["pcategory"]}","{product_info_dict["pcode"]}",{product_info_dict["product_idx"]},"{product_info_dict["create_date"]}","{product_info_dict["product_name"]}",{product_info_dict["product_price"]},"{product_info_dict["launch_date"]}","{product_info_dict["brand_name"]}",{product_info_dict["review_score"]},{product_info_dict["review_number"]},{product_info_dict["5star"]},{product_info_dict["4star"]},{product_info_dict["3star"]},{product_info_dict["2star"]},{product_info_dict["1star"]})""")
    mydb.commit()

    index_1 = 1
    for key in product_spectable:
        if key != '':
            product_spectable_dict = dict()
            product_spectable_dict["pcategory"] = checkDictValue_str(product_info,"pcategory")
            product_spectable_dict["pcode"] = checkDictValue_str(product_info,"Product_key")
            product_spectable_dict["product_idx"] = index_1
            product_spectable_dict["create_date"] = create_date
            product_spectable_dict["title"] = key
            product_spectable_dict["content"] = checkDictValue_str(product_spectable,key)
            #print(feature_rating_dict)
            cursor.execute(f"""INSERT INTO `TB_DNW_PRODUCT_DETAIL` (pcategory,pcode,product_idx,create_date,title,content) VALUES("{product_spectable_dict["pcategory"]}","{product_spectable_dict["pcode"]}",{product_spectable_dict["product_idx"]},"{product_spectable_dict["create_date"]}","{product_spectable_dict["title"]}","{product_spectable_dict["content"].replace("○","O")}")""")
            mydb.commit()
            index_1 += 1
    
    index_2 = 1
    for key in review_keyword:
        review_keyword_dict = dict()
        review_keyword_dict["pcategory"] = checkDictValue_str(product_info,"pcategory")
        review_keyword_dict["pcode"] = checkDictValue_str(product_info,"Product_key")
        review_keyword_dict["product_idx"] = index_2
        review_keyword_dict["create_date"] = create_date
        review_keyword_dict["keyword"] = checkDictValue_str(review_keyword,key)
        #print(feature_rating_dict)
        cursor.execute(f"""INSERT INTO `TB_DNW_REVIEW_KEYWORD` (pcategory,pcode,product_idx,create_date,keyword) VALUES("{review_keyword_dict["pcategory"]}","{review_keyword_dict["pcode"]}",{review_keyword_dict["product_idx"]},"{review_keyword_dict["create_date"]}","{review_keyword_dict["keyword"]}")""")
        mydb.commit()
        index_2 += 1

def insert_review_db(review):
    index_3 = 1
    for i in range(len(review)):
        review_dict = dict()
        review_dict["pcategory"] = checkDictValue_str(review[i],"pcategory")
        review_dict["pcode"] = checkDictValue_str(review[i],"product_key")
        review_dict["product_idx"] = index_3
        review_dict["create_date"] = create_date
        review_dict["rating"] = checkDictValue_str(review[i],"Rating")
        review_dict["date"] = checkDictValue_str(review[i],"Date")
        review_dict["mall"] = checkDictValue_str(review[i],"Mall")
        review_dict["title"] = checkDictValue_str(review[i],"Title")
        review_dict["content"] = checkDictValue_str(review[i],"Text")
        #print(feature_rating_dict)
        cursor.execute(f"""INSERT INTO `TB_DNW_REVIEW` (pcategory,pcode,product_idx,create_date,rating,date,mall,title,content) VALUES("{review_dict["pcategory"]}","{review_dict["pcode"]}","{review_dict["product_idx"]}","{review_dict["create_date"]}","{math.floor(int(re.sub('[가-힣]','',review_dict["rating"]))/20)}","{review_dict["date"]}","{review_dict["mall"]}","{review_dict["title"]}","{review_dict["content"]}")""")
        mydb.commit()
        index_3 += 1

# 폴더 생성 함수
def createFolder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Category
def getCategory(product_info, soup):
    categories_str = soup.select("div.location_wrap div.loca_item button")
    for list_index in range(5):
        product_info[f'Level_{list_index+1}'] = ""
    for list_index in categories_str:
        product_info[f'Level_{categories_str.index(list_index)+1}'] = list_index.get_text().strip()

# EachStarPercent
def getEachStarPercent(product_info, soup):
    for star_index in [5,4,3,2,1]:
        starPercent_html = soup.select_one(f"a#danawa-prodBlog-companyReview-score-{star_index} span.percent")
        starPercent_str = starPercent_html.get_text().strip().rstrip("%")
        product_info[f"{star_index}star"] = int(starPercent_str)

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
        reviewDict["pcategory"] = pcategory
        reviewDict["review_count"] = review_count
        reviewDict["product_key"] = pcode
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
        product_info["Product_key"] = pcode
        product_info["pcategory"] = pcategory
    except:
        pass
    try:
        # productURL
        product_info["URL"] = script_json["offers"]["url"]
    except:
        pass
    try:
        product_info["order"] = str(product_index).zfill(3)
    except:
        pass
    try:
        # Category
        getCategory(product_info, soup)
    except:
        pass
    try:
        # Name
        product_info["Name"] = script_json["name"]
    except:
        pass
    try:
        # Price
        product_info["Price"] = script_json["offers"]["lowPrice"]
    except:
        pass
    try:    
        # PriceCurrency
        product_info["PriceCurrency"] = script_json["offers"]["priceCurrency"]
    except:
        pass
    try:
        # launch date
        product_info["LaunchDate"] = soup.select_one("div.made_info").select_one("span").get_text().strip().split(":")[1].strip()
    except:
        pass
    try:
        # Brand
        product_info["BrandName"] = script_json["brand"]["name"]
    except:
        pass
    try:
        # imageURL
        product_info["ImageURL"] = script_json["image"][0]
    except:
        pass
    try:
        # description
        product_info["Description"] = script_json["description"]
    except:
        pass
    try:
        # RatingStar
        product_info["ProductRatingStar"] = float(script_json["aggregateRating"]["ratingValue"])
    except:
        pass
    try:
        # ReviewCount
        product_info["ReviewCount"] = int(script_json["aggregateRating"]["reviewCount"])
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
    # try:
    #     # ReviewText
    #     review_page = 1
    #     if review_count < REVIEW_COUNT:
    #         review_count = getRivewList(pcategory, pcode, review_page, review_count, review)
    # except:
    #     pass
    

    insert_db(product_info,product_spectable,review_keyword)
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

for pcategory in tqdm(TITLE_LIST):
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
        try:
            # Selenium && BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            # 상품을 list로 저장
            contents = soup.select("a[name='productName']")
            # 상품의 URL을 따서 goToDetailPage함수 실행
            for content in contents:
                if content_count <= CONTENT_COUNT:
                    try:      
                        detailURL = content.attrs["href"]
                        review_count = goToDetailPage(detailURL,review_count,product_index)
                        product_index += 1
                        content_count += 1
                    except:   
                        pass
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
        except:
            with open('error.txt','a') as f:
                f.write(pcategory)
                f.write("\n")