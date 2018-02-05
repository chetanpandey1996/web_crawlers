from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup

def getpage(data):
    ul = "https://www.google.com/search?q="
    uClient = Request(ul + "hotels+in+"+data, headers={'User-Agent': 'Mozilla/5.0'})
    page_html = urlopen(uClient).read()
    page_soup = soup(page_html, "html.parser")
    containers = page_soup.findAll("div", {"class": "g"})

    for container in containers:
        link = str(container.a['href'])
        if link[7:].startswith('h'):
            link = link[7:]
            if link.find('makemytrip') != -1:
                link = link[:link.index('html') + 4]
                ul = link
                break
    print(ul)
    uClient = Request(ul, headers={'User-Agent': 'Mozilla/5.0'})
    page_html = urlopen(uClient).read()
    page_soup = soup(page_html, "html.parser")
    page_val  = page_soup.find("button", {"class": "jplist-last pager-view"})
    return page_val['data-val'],ul[len(ul)-ul[::-1].index('/'):len(ul)-ul[::-1].index('.')-1]

#getpage('noida')

