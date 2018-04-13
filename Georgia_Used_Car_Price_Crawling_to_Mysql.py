
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import pickle

import bs4 as bs
import urllib.request
import json
from bs4 import BeautifulSoup
import requests
import re
from collections import Counter

import MySQLdb, pickle
from sqlalchemy import create_engine

df = pd.DataFrame(columns = ['year', 'title','brand','model','miles','photos','video','exterior_color','interior_color','transmission','drivetrain','star','review_no','vendor','price'])

for page in range(1,2):
    url = 'https://www.cars.com/for-sale/searchresults.action/?page='+str(page)+'&perPage=100&rd=99999&searchSource=PAGINATION&showMore=true&sort=relevance&stkTypId=28881&zc=31216'

    sauce = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(sauce, 'lxml')

    specificSoup = soup.find_all('div', class_='listing-row__details')



    for div in specificSoup:
        name_index = div.find('h2', {'class' :'cui-delta listing-row__title'}).text
        name = name_index.split("\n")[1]


        year_index = re.findall('[0-9]{4}',name)[0:1]
        year = year_index[0]

        title_index = name.split(" ")[29:34]
        title = " ".join(title_index)

        brand = title.split(" ")[0]

        try:
            model = title.split(" ")[1]
        except:
            model = brand

        mile_index = div.find('span', {'class' : 'listing-row__mileage'}).text
        miles = mile_index.split("\n")[0]
        regex = re.compile("\d+")
        miles = regex.findall(miles)
        miles = ''.join(miles)

        vendor_index =div.find('div',{'class' : 'listing-row__dealer-name listing-row__dealer-name-mobile'}).text
        vendor_group = vendor_index.split(' ')[0:4]

        vendor = ''
        for i in vendor_group:
            if i == '':continue
            elif re.findall('\n', i): vendor += re.sub('\n', '', i)
            else: vendor += " "+ i +" "

        photos_index = div.find('div', {'class' : 'media-count shadowed'}).text
        photos = re.findall('[0-9]{1,3}',photos_index.split("\n")[1])[0]

        video_index = div.find('div', {'class' : 'media-count shadowed'}).text
        try:
            video = re.findall('[0-9]{1,3}',photos_index.split("\n")[2])[0]
        except:
            video = 0

        exterior_color = div.find('ul', {'class' : 'listing-row__meta'}).text
        try:
            exterior_color = re.sub('\n', ' ',exterior_color).split(" ")[4]
        except:
            exterior_color = 'black'

        interior_color = div.find('ul', {'class' : 'listing-row__meta'})
        try:
            interior_color = list(interior_color)[3].text.split(" ")[3:5]
        except:
            interior_color = "black"
        interior_color = " ".join(interior_color)
        interior_color = re.sub('/' , ' ' ,interior_color)

        transmission = div.find('ul', {'class' : 'listing-row__meta'})
        try:
            transmission = list(transmission)[5].text.split(" ")[2]
        except:
            transmission = "6-speed"


        drivetrain = div.find('ul', {'class' : 'listing-row__meta'})
        try:
            drivetrain = list(drivetrain)[7].text.split(" ")[2:5]
        except:
            drivetrain = 'fwd'
        drivetrain = " ".join(drivetrain).lower()
        if drivetrain == 'rear wheel drive':
            drivetrain = 'rwd'
        elif drivetrain == 'front wheel drive':
            drivetrain = 'fwd'
        elif drivetrain == 'all wheel drive':
            drivetrain = '4wd'


        if div.find('div',{'class' : 'dealer-rating-stars'}) == None:
            star = 0
        else:
            star_index =div.find('div',{'class' : 'dealer-rating-stars'}).text
            star = star_index.split(" ")[36]
            regex = re.compile("\d")
            star = regex.findall(star)[0]


        if div.find('span',{'class' : 'listing-row__review-number'}) == None:
            review_no = 0
        else:
            review_index =div.find('span',{'class' : 'listing-row__review-number'}).text
            review_no = re.sub('\n', '',review_index.split(" ")[1])

        if div.find('span', {'class' : 'listing-row__price'}) == None:
            price = 0
        else:
            price_index = div.find('span', {'class' : 'listing-row__price'}).text
            price = price_index.split("\n")[1]
            regex = re.compile("\d")
            price = ''.join(regex.findall(price))
            price



        data = {
                'year' : year,
                'title' : title.lower(),
                'brand': brand.lower(),
                'model': model.lower(),
                'miles' : miles,
                'photos': photos,
                'video' : video,
                'exterior_color' : exterior_color.lower(),
                'interior_color' : interior_color.lower(),
                'transmission' : transmission.lower(),
                'drivetrain' : drivetrain.lower(),
                'star': star,
                'review_no' : review_no,

                'vendor' : vendor.lower(),
                'price': price,
                    }


        df.loc[len(df)] = data

df['transmission'] = df['transmission'].apply(lambda x: '6-speed' if x == 'automatic' or x == '6' else x)
df['transmission'] = df['transmission'].apply(lambda x: '8-speed' if x == '8' else x)
df['transmission'] = df['transmission'].apply(lambda x: '5-speed' if x == '5' else x)
df['transmission'] = df['transmission'].apply(lambda x: '5-speed' if x == '5' else x)
df['transmission'] = df['transmission'].apply(lambda x: 'x-speed' if x != '1-speed' and x != '2-speed' and x != '3-speed' and                                               x != '4-speed' and x != '5-speed' and x != '6-speed' and x != '7-speed' and x != '7-speed' and                                              x != '8-speed' and x != '9-speed' and x != '10-speed'                                               else x)
df['drivetrain'] = df['drivetrain'].apply(lambda x: '4wd' if x == 'four wheel drive' or x == '4wd' or x=='4x4'or x=='awd'else x)
df['drivetrain'] = df['drivetrain'].apply(lambda x: 'fwd' if x == '2wd' or x=='f w d' else x)
df['drivetrain'] = df['drivetrain'].apply(lambda x: '4wd' if x != 'fwd' and  x!='rwd' and x!='4wd' else x)

df = df[df["price"] != ""]
df = df[df["brand"] != ""]

df["year"] = df["year"].astype('int')
df["miles"] = df["miles"].astype('int')
df["photos"] = df["photos"].astype('int')
df["video"] = df["video"].astype('int')
df["star"] = df["star"].astype('int')
df["review_no"] = df["review_no"].astype('int')
df["price"] = df["price"].astype('int')

pw = pickle.load(open('./models/pw.plk','rb'))

# write local car_info
engine = create_engine("mysql+mysqldb://root:" + pw + "@13.125.22.6/used_car")
df.to_sql(name="used_car", con=engine, if_exists='replace')
