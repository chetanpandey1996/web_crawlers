from django.shortcuts import render
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import os
import re
import pickle
from nltk.corpus import stopwords
from feedbackCrawl_django.settings import BASE_DIR

review_des = []
ir=0
mr=0
tr=0
vectorizer=''
model=''
hotel_rev = dict()
cnt = 0
total_nagetive = 0;total_positive = 0
mmt_nagetive = 0;mmt_positive =0
td_nagetive =0 ; td_positive =0
bk_nagetive =0 ; bk_positive =0

def load_model():
    global vectorizer
    global model
    vectorizer = pickle.load(open(BASE_DIR + "/myapp/static/vectorizer.pkl", 'rb'))
    model = pickle.load(open(BASE_DIR + "/myapp/static/model.pkl", 'rb'))

def start_conv(data):
    global total_nagetive,total_positive
    #data = input("Enter the sentence : ")
    data = str(data)
    #data = clean(data)
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
        total_nagetive +=1
        return "Negative"
    else:
        total_positive +=1
        return "Positive"

def MMTscrapy(data):
    global mr
    global rev_des
    global hotel_rev
    global cnt
    global mmt_nagetive,mmt_positive
    ul = data
    uClient = Request(ul,headers={'User-Agent': 'Mozilla/5.0'})
    page_html = urlopen(uClient).read()
    page_soup = soup(page_html, "html.parser")
    review = []
    l = page_soup.find("div",{"id":"rmp_hotelid"})
    if(l):
        total_review_html = page_soup.find("p", {"class": "htD-reviews-overall"})
        rev = total_review_html.span.text
        rev = rev.replace(',',"")
        print(rev)
        rev = int(rev)
        print(rev)
        hotel_id = l.text
        print(hotel_id)
        print(hotel_id)
        if rev/2 > 180:
            rev = 180
        else:
            rev = int(rev/2)
        ul = "https://www.makemytrip.com/hotels/get_reviews.html?hotel_id=" + hotel_id + "&filter=all&sort_field=reviewDate&sort_order=desc&page_num=&base_path=/hotels/&hotel_no_of_reviews=" + str(
            rev)
        print(ul)
        uClient = Request(ul, headers={'User-Agent': 'Mozilla/5.0'})
        page_html = urlopen(uClient).read()
        page_soup = soup(page_html, "html.parser")
        containers = page_soup.findAll("p", {"class": "loctn_txt append_bottom10"})
        print(len(containers))
        containers_des = page_soup.findAll("p", {"class": "user_comment value_txt append_bottom20"})
        if (len(containers) > 0):
            for i in range(0, len(containers)):
                rev = containers[i].text
                rev_des = containers_des[i].text
                print(rev)
                review.append(rev)
                hotel_rev[cnt]= dict()
                hotel_rev[cnt]['name']="MakeMyTrip"
                hotel_rev[cnt]['review']=rev
                hotel_rev[cnt]['detail']=rev_des
                mr += 1
                if len(rev) > 0:
                    pred = start_conv(rev)
                else:
                    pred = start_conv(rev_des)
                if pred == "Negative":
                    mmt_nagetive +=1
                else:
                    mmt_positive +=1
                print(rev_des)
                hotel_rev[cnt]['prediction']=pred
                cnt += 1
                review_des.append(rev_des)
                print("-------------------------------------------------------------------------\n")
                review.append(rev)
        return review

def Gscrapy(data):
    global hotel_rev
    global ir
    global cnt
    global bk_positive,bk_nagetive
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
            hotel_rev[cnt] = dict()
            hotel_rev[cnt]['name'] = "Booking.com"
            hotel_rev[cnt]['review'] = rev
            hotel_rev[cnt]['detail'] = "none"
            review.append(rev)
            ir +=1
            pred = start_conv(rev)
            if pred == "Negative":
                bk_nagetive +=1
            else:
                bk_positive +=1
            hotel_rev[cnt]['prediction'] = pred
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
    global td_nagetive,td_positive
    ul = data
    uClient = Request(ul, headers={'User-Agent': 'Mozilla/5.0'})
    page_html = urlopen(uClient).read()
    page_soup = soup(page_html, "html.parser")
    # containers = page_soup.findAll("div", {"class": "quote"})
    rev_html = page_soup.findAll("b")
    rev_no = str(rev_html[3])
    rev_no = rev_no[rev_no.index('>') + 1:len(rev_no) - (rev_no[::-1].index('<')) - 1]
    i = 5
    rev_no = rev_no.replace(',', "")
    pages = int(rev_no)
    if (pages > 180):
        pages = 180
    review = []
    containers = page_soup.findAll("span", {"class": "noQuotes"})
    containers1 = page_soup.findAll("p", {"class": "partial_entry"})
    for j in range(0, len(containers)):
        rev = containers[j].text
        rev_des = containers1[j].text
        review.append(rev)
        hotel_rev[cnt] = dict()
        hotel_rev[cnt]['name'] = "TripAdvisor"
        hotel_rev[cnt]['review'] = rev
        hotel_rev[cnt]['detail'] = rev_des
        print(rev)
        tr += 1
        pred = start_conv(rev)
        if pred == "Negative":
            td_nagetive += 1
        else:
            td_positive += 1
        hotel_rev[cnt]['prediction'] = pred
        print(rev_des)
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
            hotel_rev[cnt] = dict()
            hotel_rev[cnt]['name'] = "TripAdvisor"
            hotel_rev[cnt]['review'] = rev
            hotel_rev[cnt]['detail'] = rev_des
            review.append(rev)
            tr += 1
            pred = start_conv(rev)
            if pred == "Negative":
                td_nagetive += 1
            else:
                td_positive += 1
            hotel_rev[cnt]['prediction'] = pred
            print(rev_des)
            cnt += 1
            print("------------------------------\n")
        page_html = ""
        page_soup = ""
        containers = ""
        i = i + 5
    return review

def search(data):
    load_model()
    ul = "https://www.google.com/search?q="
    uClient = Request(ul+data,headers={'User-Agent': 'Mozilla/5.0'})
    page_html = urlopen(uClient).read()
    page_soup = soup(page_html, "html.parser")
    containers = page_soup.findAll("div", {"class": "g"})
    urls = []
    m = 1
    t = 1
    b = 1
    for container in containers:
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
    feeds = []
    for url in urls:
        if url.find('makemytrip') != -1:
            feeds.append(MMTscrapy(url))
        elif url.find('tripadvisor') != -1:
            feeds.append(TAscrapy(url))
        elif url.find('booking') != -1:
            url = url[len(url) - url[::-1].index('/'):len(url) - url[::-1].index('.') - 1]
            print(url)
            feeds.append(Gscrapy(url))

    print(ir + mr + tr)
    return feeds
# Create your views here.
def index_view(request):
    global review_des
    if request.method == 'POST':
        print('inside')
        name = request.POST.get('name')
        place = request.POST.get('place')

        search_string = name + ' '+place+"  hotel Reviews"
        search_string = search_string.replace(' ','+')
        feeds = search(search_string)
        hotel_rev['total_rev']=total_nagetive+total_positive
        hotel_rev['total_pos']=total_positive
        hotel_rev['total_neg']=total_nagetive
        hotel_rev['mmt_neg']=mmt_nagetive
        hotel_rev['mmt_pos']=mmt_positive
        hotel_rev['td_neg']=td_nagetive
        hotel_rev['td_pos']=td_positive
        hotel_rev['bk_neg']=bk_nagetive
        hotel_rev['bk_pos']=bk_positive
        return render(request, 'index.html',{'feeds': hotel_rev})
    else:
        return render(request, 'index.html')