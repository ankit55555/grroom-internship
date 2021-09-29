import urllib.request as ur
import json 
import csv
from bs4 import BeautifulSoup as bs
import requests as rs
import math
import time
import sqlite3

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent':user_agent}

conn = sqlite3.connect('Pantaloons.db')
c = conn.cursor()

c.execute('''CREATE TABLE product_details
            (Website varchar(40) not null,
            Product_Link text PRIMARY KEY,
            Product_Name varchar(50) not null,
            Product_Brand varchar(50) not null,
            Product_Category varchar(50) not null,
            Size_Avail varchar(20) not null,
            Price int not null,
            MRP int not null,
            Gender varchar(15) not null,
            Description text not null,
            Primary_Image_Links text not null,
            Secondary_Image_Links text not null,
            Affiliate_Link text not null )''')
            
urls = [
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=455&category_name=collections&strCatDisplayName=Pantaloons%20Collection&gender_name=Home&strCatName=collections&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&fp=Gender__fq%3AMen%7CCategorygroupid__fq%3A51&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=455&category_name=collections&strCatDisplayName=Pantaloons%20Collection&gender_name=Home&strCatName=collections&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&fp=Gender__fq%3AMen%7CCategorygroupid__fq%3A52&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=200&category_name=active-wear&strCatDisplayName=Active%20Wear%20for%20Men&gender_name=Men&strCatName=active-wear&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=198&category_name=ethnic&strCatDisplayName=Ethnic%20Wear%20for%20Men&gender_name=Men&strCatName=ethnic&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=483&category_name=collections&strCatDisplayName=Latest%20Fashion%20Outfits&gender_name=Home&strCatName=collections&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=asc&fp=Category__fq%3AMasks%7CGender__fq%3AMen%7CGender__fq%3AUnisex&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=5183&category_name=inner-wear&strCatDisplayName=Innerwear%20for%20Men&gender_name=Men&strCatName=inner-wear&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=196&category_name=footwear&strCatDisplayName=Footwear%20for%20Men&gender_name=Men&strCatName=footwear&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=455&category_name=collections&strCatDisplayName=Pantaloons%20Collection&gender_name=Home&strCatName=collections&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&fp=Gender__fq%3AWomen%7CCategorygroupid__fq%3A53&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=455&category_name=collections&strCatDisplayName=Pantaloons%20Collection&gender_name=Home&strCatName=collections&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&fp=Gender__fq%3AWomen%7CCategorygroupid__fq%3A54&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=1958&category_name=plus-size&strCatDisplayName=Plus%20Size%20for%20Women&gender_name=Women&strCatName=plus-size&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=887&category_name=sleepwear&strCatDisplayName=Sleepwear%20for%20Women&gender_name=Women&strCatName=sleepwear&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=224&category_name=active-wear&strCatDisplayName=Active%20Wear%20for%20Women&gender_name=Women&strCatName=active-wear&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=483&category_name=collections&strCatDisplayName=Latest%20Fashion%20Outfits&gender_name=Home&strCatName=collections&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=asc&fp=Category__fq%3AMasks%7CGender__fq%3AWomen%7CGender__fq%3AUnisex&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=992&category_name=inner-wear&strCatDisplayName=Innerwear%20for%20Women&gender_name=Women&strCatName=inner-wear&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=215&category_name=footwear&strCatDisplayName=Footwear%20for%20Women&gender_name=Women&strCatName=footwear&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1',
    'https://www.pantaloons.com/cat/fetchLefProductsWRTPage?category_id=5503&category_name=handbags&strCatDisplayName=Handbags%20%26amp%3B%20Backpacks&gender_name=Women&strCatName=handbags&strShopName=Pantaloons&intShopID=8&outofstock=&orderby=position&orderway=desc&intPageNo={pgn}&from={from_}&pageSize=24&actiontype=refresh&hdnLoad=1'
]            

for iu in range(len(urls)):
    base_url = urls[iu]
    s_url = base_url.format(pgn=1, from_=0)
    rq = ur.Request(s_url, None, headers)
    res = ur.urlopen(rq)
    data = res.read() 
    data = json.loads(data)
    tpg = data['TotalProductsCount']
    print(tpg)
    pgc = math.ceil(tpg/24)
    pgn = 1
    from_ = 0
    print(pgc)
    for i in range(1, pgc+1):
        try:
            time.sleep(0.8)
            nurl = base_url.format(pgn = pgn, from_ = from_)
            req = rs.get(nurl, headers=headers)
            data1 = json.loads(req.text)
            pgn = pgn + 1
            from_ = from_ + 24
            prod = data1['Products']['Results']['hits']['hits']
            for p in prod:
                web = 'https://www.pantaloons.com/'
                src = p['_source']
                name = src['LinkRewrite']
                id_ = p['_source']['ProductID']
                link = "https://www.pantaloons.com/p/{n}-{i}.html".format(n=name, i=id_)
                print(link)
                brand = src['Features']['Subbrand']
                prcat = src['DefaultCategoryName']
                sizes = []
                szs = src['Sizes']
                for s in szs:
                    if (s['Quantity'] != 0):
                        sizes.append(str(s['Name']))
                sizes = ', '.join(sizes)
                sizes = sizes.replace('/', ', ')
                price = src['SellingPrice']
                mrp = src['Price']
                gender = src['Gender']
                description = src['Description']
                images = src['Media']['Images']
                priimg = ''
                secimg = ''
                #base_url_img = 'https://pantaloons.imgix.net/img/app/product/{l}/{Name}.jpg'
                iid = str(id_)[0]
                name1 = images[0]['Name']
                name2 = images[1]['Name']
                priimg = 'https://pantaloons.imgix.net/img/app/product/'+iid+'/'+str(name1)+".jpg"
                secimg = 'https://pantaloons.imgix.net/img/app/product/'+iid+'/'+str(name2)+".jpg"
                afl = ''
                #print(web, link, name, brand, prcat, sizes, price, mrp, gender, description, priimg, secimg, afl)
                c.execute('''INSERT INTO product_details VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (web, link, name, brand, prcat, sizes, price, mrp, gender, description, priimg, secimg, afl))
                conn.commit()
                #csv_writer.writerow([web, link, name, brand, prcat, sizes, price, mrp, gender, description, priimg, secimg, afl])
        except Exception as e:
            print(e)
            continue
    print(iu+1)
conn.close()

