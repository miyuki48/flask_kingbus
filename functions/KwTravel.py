
import requests
from bs4 import BeautifulSoup
import pandas as pd

def crawlerKwTravel():
    url = "https://kw-travel.com.tw/"
    my_header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
    
    resp = requests.get(url,headers = my_header)
    
    urlList = []
    picList = []
    titleList = []
    priceList = []
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text,"html.parser")
        urls = soup.select("#main div.col-lg-3.col-6.mb-4.px-1.px-sm-2 div.card-footer.px-0 a")
        pics = soup.select("#main div.col-lg-3.col-6.mb-4.px-1.px-sm-2 div.card.h-100 img")
        titles = soup.select("#main div.col-lg-3.col-6.mb-4.px-1.px-sm-2 div.card-body.px-0 h6")
        prices = soup.select("#main div.col-lg-3.col-6.mb-4.px-1.px-sm-2 div.card-footer.px-0")
        
        for url,pic,title,price in zip(urls,pics,titles,prices):
            urlList.append(url.get("href"))
            picList.append(pic.get("src"))
            titleList.append(title.text)
            priceList.append(price.text)
            
        df = pd.DataFrame({"title":titleList,"url":urlList,
                           "price":priceList,"pic":picList})
        return df
        
if __name__ == "__main__":
    df = crawlerKwTravel()












