#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 20:28:58 2021

@author: jiahuiwu
"""

from GoogleNews import GoogleNews
from newspaper import Article
import pandas as pd
from newspaper import Config
import nltk

nltk.download('punkt')

User_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
config = Config()
config.browser_user_agent = User_agent

googlenews=GoogleNews(start='01/01/2018',end='12/31/2018')
googlenews.search('New York Taxi')
result=googlenews.result()
df = pd.DataFrame(result)

for i in range(2,30):
    googlenews.getpage(i)
    result=googlenews.result()
    df = pd.DataFrame(result)
    print(len(df))

df.to_csv('GoogleNews.csv')


news_list = []
for ind in df.index:
    Dict ={}
    article = Article(df['link'][ind],config=config)
    article.download()
    article.parse()
    article.nlp()
    Dict['Date']=df['date'][ind]
    Dict['Media']=df['media'][ind]
    Dict['Title']=article.title
    Dict['Article']=article.text
    Dict['Summary']=article.summary
    news_list.append(Dict)
news_df=pd.DataFrame(news_list)
news_df.to_csv("GGnews.csv")




from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer(min_df=0, stop_words="english", max_features=200)
all_words = ''
for i in range(0,len(news_df['Article'])):
    all_words = all_words + news_df['Article'][i]

Vector = cv.fit_transform([all_words]).toarray().tolist()[0]
word = cv.get_feature_names()
count = {w:v for w,v in zip(word,Vector)}

count.pop('key', None)
count.pop('taxi',None)
count.pop('city',None)
count.pop('drivers',None)
count.pop('york',None)

from wordcloud import WordCloud

wordcloud = WordCloud(background_color='white').fit_words(count)

import matplotlib.pyplot as plt

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
plt.savefig('/Users/jiahuiwu/Desktop/501/portfolio/picture/wordcloud.png')
