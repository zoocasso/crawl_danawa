from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json
import os

# 폴더 생성 함수
def createFolder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Category
def getCategory(infoDict, soup):
    categories_str = soup.select("div.location_wrap div.loca_item button")
    for list_index in range(5):
        infoDict[f'Level_{list_index+1}'] = ""
    for list_index in categories_str:
        infoDict[f'Level_{categories_str.index(list_index)+1}'] = list_index.get_text().strip()

# EachStarPercent
def getEachStarPercent(infoDict, soup):
    for star_index in [5,4,3,2,1]:
        starPercent_html = soup.select_one(f"a#danawa-prodBlog-companyReview-score-{star_index} span.percent")
        starPercent_str = starPercent_html.get_text().strip().rstrip("%")
        infoDict[f"{star_index}star"] = int(starPercent_str)

# ReviewKeyword
def getReviewKeyword(infoDict, soup):
    reviewKeyword_list = soup.select_one("ul.tag_list").select("li")[1:]
    index = 1
    for reviewKeyword in reviewKeyword_list:
        infoDict[f"ReviewKeyword_{index}"] = reviewKeyword.get_text().strip()
        index += 1

def getRivewList(pcode, review_page, review_count, reviewList):
    review_count = getReviewText(pcode,review_count, reviewList)
    while True:
        if review_count > REVIEW_COUNT:
            break
        try:
            review_page += 1
            driver.find_element(By.CSS_SELECTOR,f"a[data-pagenumber = '{review_page}']").click()
            time.sleep(0.5)
            review_count = getReviewText(pcode,review_count,reviewList)
        except:
            break
    return review_count

def getReviewText(pcode,review_count, reviewList):
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
        reviewDict["review_count"] = review_count
        reviewDict["product_key"] = pcode
        reviewDict["category_key"] = category_key
        reviewDict["Rating"] = Rating
        reviewDict["Date"] = Date
        reviewDict["Mall"] = Mall
        reviewDict["Title"] = Title
        reviewDict["Text"] = Text
        reviewList.append(reviewDict)
        review_count += 1
    return review_count

# SpecTable
def getSpecTable(specTableDict, soup):
    specTable_key = soup.select("table.spec_tbl tbody tr th.tit")
    specTable_value = soup.select("table.spec_tbl tbody tr td.dsc")
    specTable_key_list = list()
    specTable_value_list = list()
    for list_index in specTable_key:
        specTable_key_list.append(list_index.get_text().strip())
    for list_index in specTable_value:
        specTable_value_list.append(list_index.get_text().strip().replace("\n","").replace("\t","").rstrip("(제조사 웹사이트 바로가기)"))
    specTable_key_list = list(filter(None, specTable_key_list))
    specTable_value_list = list(filter(None, specTable_value_list))
    for list_index in range(len(specTable_key)):
        specTableDict[specTable_key_list[list_index]] = specTable_value_list[list_index]

# 상품 정보페이지로 넘어가는 함수
def goToDetailPage(detailURL,content_count,review_count,product_index):
    
    infoDict = dict()
    specTableDict = dict()
    # Selenium
    driver.get(detailURL)
    time.sleep(1)
    page_source = driver.page_source
    # BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    script_str = soup.find("script", type="application/ld+json")
    script_json = json.loads(script_str.get_text())
    try:       
        # Product Key
        pcode = script_json["sku"]
        infoDict["Product_key"] = pcode
        infoDict["category_key"] = category_key
    except:
        pass
    try:
        # productURL
        infoDict["URL"] = script_json["offers"]["url"]
    except:
        pass
    try:
        infoDict["order"] = str(product_index).zfill(3)
    except:
        pass
    try:
        # Category
        getCategory(infoDict, soup)
    except:
        pass
    try:
        # Name
        infoDict["Name"] = script_json["name"]
    except:
        pass
    try:
        # Price
        infoDict["Price"] = script_json["offers"]["lowPrice"]
    except:
        pass
    try:    
        # PriceCurrency
        infoDict["PriceCurrency"] = script_json["offers"]["priceCurrency"]
    except:
        pass
    try:
        # launch date
        infoDict["LaunchDate"] = soup.select_one("div.made_info").select_one("span").get_text().strip().split(":")[1].strip()
    except:
        pass
    try:
        # Brand
        infoDict["BrandName"] = script_json["brand"]["name"]
    except:
        pass
    try:
        # imageURL
        infoDict["ImageURL"] = script_json["image"][0]
    except:
        pass
    try:
        # description
        infoDict["Description"] = script_json["description"]
    except:
        pass
    try:
        # RatingStar
        infoDict["ProductRatingStar"] = float(script_json["aggregateRating"]["ratingValue"])
    except:
        pass
    try:
        # ReviewCount
        infoDict["ReviewCount"] = int(script_json["aggregateRating"]["reviewCount"])
    except:
        pass
    try:
        # EachStarPercent
        getEachStarPercent(infoDict, soup)
    except:
        pass
    try:
        # ReviewKeyword
        getReviewKeyword(infoDict, soup)
    except:
        pass
    try:
        # ReviewText
        review_page = 1
        if review_count<REVIEW_COUNT:
            review_count = getRivewList(pcode, review_page, review_count, reviewList)
    except:
        pass
    try:
        # SpecTable
        getSpecTable(specTableDict, soup)
    except:
        pass
    
    #########크롤링한 결과물을 json으로 저장
    createFolder(f'./result/index{str(content_count).zfill(3)}_{script_json["sku"]}')
    
    with open(f'./result/index{str(content_count).zfill(3)}_{script_json["sku"]}/infoDict.json','w',encoding='utf-8') as f:
        json.dump(infoDict,f,indent=4, ensure_ascii=False)
    # print(infoDict)

    with open(f'./result/index{str(content_count).zfill(3)}_{script_json["sku"]}/specTableDict.json','w',encoding='utf-8') as f:
        json.dump(specTableDict,f,indent=4, ensure_ascii=False)
    # print(specTableDict)

    with open(f'./result/reviewList.json','w',encoding='utf-8') as f:
        json.dump(reviewList,f,indent=4, ensure_ascii=False)
    # print(reviewList)

    return review_count

# 다음 페이지로 넘기는 함수
def goToNextPage(cur_page,soup):
    page_html = soup.select("div.number_wrap a")
    for index in page_html:
        isNextPage = int(index.get_text())
        if isNextPage > cur_page:
            cur_page = isNextPage
            driver.get(URL_ADDRESS + URL_PREFIX + category_key)
            driver.execute_script("movePage(%s)" % cur_page)
            return cur_page
        else:
            continue
    pageElement = soup.select_one("a.paging_edge_nav.paging_nav_next")
    isNextPage = pageElement.get_text()
    if isNextPage == "다음 페이지":
        cur_page += 1
        driver.get(URL_ADDRESS + URL_PREFIX + category_key)
        driver.execute_script("getPage(%s)" % cur_page)
        return cur_page

options = Options()
driver = webdriver.Firefox(options=options)
driver.set_window_size(1920, 1080)

URL_ADDRESS = "https://search.danawa.com/dsearch.php?k1="
URL_PREFIX = ""
CONTENT_COUNT = 1000
REVIEW_COUNT = 20000
input_txt = open("./input.txt","r", encoding="utf-8")
TITLE_LIST = input_txt.read().splitlines()

for category_key in TITLE_LIST:
    content_count = 1
    review_count = 1
    cur_page = 1
    product_index = 1
    isdone = False
    reviewList = list()

    driver.get(URL_ADDRESS + URL_PREFIX + category_key)
    
    while(True):
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR,"li[data-view-method='list'] a").click()
        time.sleep(2)
        # Selenium && BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        # 상품을 list로 저장
        contents = soup.select("a.click_log_product_standard_title_")
        # 상품의 URL을 따서 goToDetailPage함수 실행
        print(0)
        for content in contents:
            print(1)
            if content_count <= CONTENT_COUNT:
                print(2)
                # try:      
                detailURL = content.attrs["href"]
                review_count = goToDetailPage(detailURL,content_count,review_count,product_index)
                product_index += 1
                content_count += 1

                # except:
                #     pass
            else:
                isdone = True
                break
        if isdone == True:
            break

        # 페이지 넘기는 함수
        cur_page = goToNextPage(cur_page, soup)
        
    if isdone == True:
        break