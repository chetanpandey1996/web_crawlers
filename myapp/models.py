from django.db import models

from pymongo import MongoClient
import pageno as pg
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import base64
import json
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import os
import re
import pickle
from nltk.corpus import stopwords
from feedbackCrawl_django.settings import BASE_DIR

'''
city_name = ''
hotel_name = ''
ir = 0
mr = 0
tr = 0
vectorizer = ''
model = ''
cnt = 0
total_nagetive = 0;
total_positive = 0
mmt_nagetive = 0;
mmt_positive = 0
td_nagetive = 0;
td_positive = 0
bk_nagetive = 0;
bk_positive = 0

client = MongoClient('localhost', 27017)
db = client['feedback']
collection = db['places']


def insert_data(by, title, description, prediction):
    global city_name, hotel_name
    collection = db[city_name]
    collection.update({'name':hotel_name }, {
        '$push': {'data': {'from': by, 'head': title, 'detail': description, 'prediction': prediction}}})


def load_model():
    global vectorizer
    global model
    vectorizer = pickle.load(open(BASE_DIR + "/myapp/static/vectorizer.pkl", 'rb'))
    model = pickle.load(open(BASE_DIR + "/myapp/static/model.pkl", 'rb'))


def start_conv(data):
    global total_nagetive, total_positive
    # data = input("Enter the sentence : ")
    data = str(data)
    # data = clean(data)
    review = re.sub('[^a-zA-Z]', ' ', data)
    review = review.lower()
    review = review.split()
    review = [word for word in review if not word in set(stopwords.words('english'))
              or word == 'not']
    review = ' '.join(review)
    data = review
    x = vectorizer.transform([data]).toarray()
    y_pred = model.predict(x)
    if y_pred == 0:
        total_nagetive += 1
        return "Negative"
    else:
        total_positive += 1
        return "Positive"

#====================================================================================================================
def MMTscrapy(data):
    global city_name, hotel_name
    global mr
    global rev_des
    global hotel_rev
    global cnt
    global mmt_nagetive, mmt_positive
    collection = db[city_name]

    ul = data
    uClient = Request(ul, headers={'User-Agent': 'Mozilla/5.0'})
    page_html = urlopen(uClient).read()
    page_soup = soup(page_html, "html.parser")

    l = page_soup.find("div", {"id": "rmp_hotelid"})

    if not l == None:
        total_review_html = page_soup.find("p", {"class": "htD-reviews-overall"})
        rev = total_review_html.span.text
        rev = rev.replace(',', "")
        print(rev)
        rev = int(rev)
        print(rev)
        hotel_id = l.text
        print(hotel_id)
        print(hotel_id)
        if rev > 180:
            rev = 180

        ul = "https://dtr-hoteldom.makemytrip.com/mmthtl/site/getMoreReviewsNew?hotelId=" + hotel_id + "&country=IN&type=MMT&numReviews=" + str(
            rev) + "&sort=D&start=0"
        print(ul)
        uClient = Request(ul, headers={'User-Agent': 'Mozilla/5.0'})
        page_html = urlopen(uClient).read()

        json_data = json.loads(page_html.decode(encoding='UTF-8'))

        re_list = json_data['review_list']
        for review in re_list:
            rev = review['title']
            rev_des = review['description']
            print('- ' * 20)
            if len(rev) > 0:
                pred = start_conv(rev)
            else:
                pred = start_conv(rev_des)
            if pred == "Negative":
                mmt_nagetive += 1
            else:
                mmt_positive += 1
            print(rev_des)
            insert_data("MakeMyTrip", rev, rev_des, pred)
            cnt += 1
            print("-------------------------------------------------------------------------\n")
    collection.update({'name':hotel_name}, {
        '$set': {'mmt': {'Totalp': mmt_positive, 'Totaln': mmt_nagetive}}})
    return None


def Gscrapy(data):
    global hotel_rev
    global ir
    global cnt
    global bk_positive, bk_nagetive
    review = []
    driver = webdriver.Firefox()
    ul1 = "https://www.booking.com/reviewlist.html?;pagename="
    ul2 = ";cc1=in;type=total;score=;dist=1;rows=100;r_lang=en"
    driver.get(ul1 + data + ul2)
    try:
        body_text = driver.page_source
        page_soup = soup(body_text, "html.parser")
        containers = page_soup.findAll("div", {"class": "review_item_header_content_container"})
        review = []
        for container in containers:
            rev = (container.div.text).strip()
            print(rev)
            review.append(rev)
            ir += 1
            rev_des = 'none'
            pred = start_conv(rev)
            if pred == "Negative":
                bk_nagetive += 1
            else:
                bk_positive += 1
            insert_data("Booking.com", rev, rev_des, pred)
            cnt += 1
            print("-----------------------------------------------------\n")
    except TimeoutException:
        print("Box or Button not found in google.com")
    time.sleep(5)
    driver.quit()
    return review


def TAscrapy(data):
    global hotel_rev
    global tr
    global cnt
    global td_nagetive, td_positive
    global city_name, hotel_name
    collection = db[city_name]

    ul = data
    uClient = Request(ul, headers={'User-Agent': 'Mozilla/5.0'})
    page_html = urlopen(uClient).read()
    page_soup = soup(page_html, "html.parser")
    # containers = page_soup.findAll("div", {"class": "quote"})
    rev_html = page_soup.findAll("b")
    if rev_html and len(rev_html) >= 3:
        rev_no = str(rev_html[3])
        rev_no = rev_no[rev_no.index('>') + 1:len(rev_no) - (rev_no[::-1].index('<')) - 1]
        i = 5
        rev_no = rev_no.replace(',', "")
        pages = int(rev_no)
        if (pages > 180):
            pages = 180

        containers = page_soup.findAll("span", {"class": "noQuotes"})
        containers1 = page_soup.findAll("p", {"class": "partial_entry"})
        for j in range(0, len(containers)):
            rev = containers[j].text
            rev_des = containers1[j].text
            print(rev)
            tr += 1
            pred = start_conv(rev)
            if pred == "Negative":
                td_nagetive += 1
            else:
                td_positive += 1
            print(rev_des)
            insert_data("TripAdvisor", rev, rev_des, pred)
            print("------------------------------\n")
        ul_half1 = ul[0:ul.index("Reviews") + 8]
        ul_half2 = ul[ul.index("Reviews") + 7:len(ul)]
        cnt += 1
        while i <= pages:
            uClient = Request(ul_half1 + "or" + str(i) + ul_half2, headers={'User-Agent': 'Mozilla/5.0'})
            page_html = urlopen(uClient).read()
            page_soup = soup(page_html, "html.parser")
            containers = page_soup.findAll("span", {"class": "noQuotes"})
            containers1 = page_soup.findAll("p", {"class": "partial_entry"})
            for j in range(0, len(containers)):
                rev = containers[j].text
                rev_des = containers1[j].text
                print(rev)
                tr += 1
                pred = start_conv(rev)
                if pred == "Negative":
                    td_nagetive += 1
                else:
                    td_positive += 1
                print(rev_des)
                insert_data("TripAdvisor", rev, rev_des, pred)
                cnt += 1
                print("------------------------------\n")
            page_html = ""
            page_soup = ""
            containers = ""
            i = i + 5
    collection.update({'name':hotel_name}, {
        '$set': {'tda': {'Totalp': td_positive, 'Totaln': td_nagetive}}})
    return None


def search(data):
    ul = "https://www.google.com/search?q="
    uClient = Request(ul + data, headers={'User-Agent': 'Mozilla/5.0'})
    page_html = urlopen(uClient).read()
    page_soup = soup(page_html, "html.parser")
    containers = page_soup.findAll("div", {"class": "g"})
    urls = []
    m = 1
    t = 1
    b = 1
    for container in containers:
        if container.a:
            link = str(container.a['href'])
            if link[7:].startswith('h'):
                link = link[7:]
                print(link)
                if link.find('makemytrip') != -1 and t != 0:
                    link = link[:link.index('html') + 4]
                    urls.append(link)
                    t = 0
                if link.find('tripadvisor') != -1 and m != 0:
                    link = link[:link.index('html') + 4]
                    urls.append(link)
                    m = 0
                elif link.find('booking') != -1 and b != 0:
                    link = link[:link.index('&')]
                    urls.append(link)
                    b = 0
            print(urls)

    for url in urls:
        if url.find('makemytrip') != -1:
            MMTscrapy(url)
        elif url.find('tripadvisor') != -1:
            TAscrapy(url)
        elif url.find('booking') != -1:
            url = url[len(url) - url[::-1].index('/'):len(url) - url[::-1].index('.') - 1]
            #Gscrapy(url)

    print(ir + mr + tr)
    return None



name = input("enter city name : ")
while name != 'no':
    collection.update({},{"$push":{'name':name}});
    name = input("enter the city : ")

da = collection.find()
for d in da:
    for dt in d['name']:
        j = 0
        if dt == 'noida' or dt == 'delhi':
            continue
        collection = db[dt]
        page  = pg.getpage(dt)
        print(page[0])
        print(page[1])
        p=''
        i = 1
        while i <= int(page[0]):
            url = "https://www.makemytrip.com/seo-api/hotels/api/hotels/list?propertyType=&city=" + dt + "&area=&amenity=&star=&traveller=&attraction=&country=india&chainUrlPhrase=&page=" + str(p) + "&hotelId=&pathName=%2Fhotels%2F"+dt+"-hotels.html&templateType=city_template&sortType=POPULARTITY"
            print(url)

            uClient = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            page_html = urlopen(uClient).read()
            page_soup = soup(page_html, "html.parser")
            #print(page_soup)
            hotel_names = page_soup.findAll("a", {"class": "hotel-title"})
            for name in hotel_names:
                name = name.text
                name = name.replace('\n','')
                name = name.replace('.','') 
                collection.insert({'name':name,'data':[],'mmt':'','tda':'','total':''})
            p =i
            i +=1


da  = collection.find()
for d in da:
   for de in d.keys():
       print(de)


da = collection.find()
load_model()
for d in da:
    for city_name in d['name']:
        if city_name == 'manali' or city_name == 'shimla' or city_name == 'hyderabad':
            continue
        print('---------------------------\n')
        print(city_name)
        print('-'*20)
        collection = db[city_name]
        data = collection.find()

        for d in data:
            hotel_name = d['name']
            if not hotel_name.startswith('_'):
                    print(hotel_name)
                    search_data = hotel_name + ' ' + city_name + ' hotel reviews'
                    search_data = search_data.replace(' ', '+')
                    search(search_data)
                    collection.update({'name': hotel_name}, {
                        '$set': {'total': {'positive': total_positive, 'negative': total_nagetive}}})

'''


