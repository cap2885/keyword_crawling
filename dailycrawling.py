import pandas as pd 
import collections
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import requests

import math
from datetime import datetime 
from datetime import datetime, timedelta


from powernad.API.Campaign import *
from powernad.API.RelKwdStat import *

import time

from time import sleep
from urllib.error import HTTPError

import urllib.request
from datetime import datetime, timedelta
import json

from tqdm.notebook import tqdm

# time_month는 오늘부터 한달전 날짜
toda = datetime.now()
time_month = toda - relativedelta(months=1)
time_month = time_month.strftime('%Y-%m-%d')
time_month= str(time_month)

yesterday = toda - relativedelta(days=1)
yesterday = yesterday.strftime('%Y-%m-%d')
yesterday = str(yesterday)

today = str(datetime.now().date())

dt_index = pd.date_range(start=time_month, end = yesterday)


date = pd.DataFrame(data=dt_index, columns=['날짜'])

BASE_URL = 'https://api.naver.com'
API_KEY = '010000000024c9e5a9b1b62f0a416494d8bbcc3ad0fb03a7e2bc8299c0efa47f6b777cc5d2'
SECRET_KEY = 'AQAAAAAkyeWpsbYvCkFklNi7zDrQa4271M1lEsIRsn+oPzSosA=='
CUSTOMER_ID = '2687618'

rel = RelKwdStat(BASE_URL, API_KEY, SECRET_KEY, CUSTOMER_ID)

def search_keyword(searchword):
    

    kwdDataList = rel.get_rel_kwd_stat_list(siteId=None, biztpId=None, hintKeywords=searchword, event=None, month=None, showDetail='1')


    kwd_result = (kwdDataList[0].relKeyword, #키워드
                 kwdDataList[0].monthlyPcQcCnt, #월간 검색수 (PC)
                 kwdDataList[0].monthlyMobileQcCnt, # 월간 검색수 (Mobile)
                 kwdDataList[0].monthlyPcQcCnt+kwdDataList[0].monthlyMobileQcCnt) # 월간 total 
    return(kwd_result[3])

client_id = "rlO91TuiZuxx0AO10NzS" 
client_secret = "LlhnYvZ2q9"

dictionary_yester={}
dictionary_now={}

# lis = ['검색하고자 하는 키워드 입력']
lis = ['토트넘']

error=[]
for i in tqdm(lis):  
    sleep(1)
    try:
        if type(search_keyword(i)) !=str : 
            searchword = i.replace(" ","")
            month_total = search_keyword(searchword)
            print(month_total)

            url = "https://openapi.naver.com/v1/datalab/search"
            body = "{\"startDate\":\""+time_month+"\",\"endDate\":\""+today+"\",\"timeUnit\":\"date\",\"keywordGroups\":[{\"groupName\":\""+i+"\",\"keywords\":[\""+i+"\"]}]}";
            requested = urllib.request.Request(url)
            requested.add_header("X-Naver-Client-Id", client_id)
            requested.add_header("X-Naver-Client-Secret", client_secret)
            requested.add_header("Content-Type", "application/json")
            response = urllib.request.urlopen(requested, data=body.encode("utf-8"))
            rescode = response.getcode()

            if(rescode==200):
                response_body = response.read()
                output_data = response_body.decode('utf-8')
            else:
                print('Error code:'+ rescode)
                pass

            result = json.loads(output_data)

            date = [month_total['period'] for month_total in result['results'][0]['data']]
            ratio = [month_total['ratio'] for month_total in result['results'][0]['data']]
            ratio_tm = pd.DataFrame({'date':date, 
                          i:ratio,
                          })

            # 일일 데이터 계산 
            sleep(0.5)
            total = ratio_tm[i].sum()
            print(total)
            ratio_tm[i] = ratio_tm[i].apply(lambda x :((x / total)*float(month_total)))
            print(ratio_tm[i])
        else : 
            pass

    except (TypeError, IndexError,KeyError,ValueError):
        print(" 타입 or 인덱스 에러,Value 에러:",i)
        error.append(i)
        pass


    except HTTPError:
        print('http 에러:', i )
        error.append(i)
        pass

        #여기부터 새로코딩함 
    try: 
        if type(search_keyword(i)) !=str : 
            searchword = i.replace(" ","")
            month_total = search_keyword(searchword)        

            dt_index = pd.date_range(start=time_month, end= yesterday)
            dt_list = dt_index.strftime("%Y-%m-%d").tolist()

            date = pd.DataFrame(data=dt_list, columns=['날짜'])

            spred = pd.merge(date,ratio_tm,left_on='날짜',right_on='date',how='outer')
            spred.drop(['date'],inplace=True, axis=1)

            spred.replace(np.nan,0,inplace=True)


            month_total=[] 

            for j in range(len(spred)) : 
                month_total.append(today)


            spred['수집날짜'] = month_total

            spred = spred[['날짜','수집날짜',i]]

            if i in dictionary_yester:

                pass

            else : 
                dictionary_yester[i]=[]



            dictionary_now[i]=spred

        else:
            pass

    except (TypeError, IndexError,KeyError,ValueError):

        pass

    sleep(0.5)
    try :
        if type(search_keyword(i)) !=str : 
            searchword = i.replace(" ","")
            month_total = search_keyword(searchword)        

            if dictionary_yester[i]==[]:
                dictionary_yester[i] = dictionary_now[i]
               # for k in range(3):
                #    sleep(1)
                 #   gc2.append_row(dictionary_now[i].iloc[-1-k,:].values.tolist()+[i])


            else : 
                pass 
        else:
            pass


    except (TypeError, IndexError,KeyError):
          pass

    except ValueError:


            yester_df= dictionary_yester[i]
            today_df = dictionary_now[i]


            yester_df.set_index('날짜',inplace=True)

            today_df.set_index('날짜',inplace=True)

            yester_df.update(today_df)


            tmpt = today_df.iloc[-1,:]

            yester_df = yester_df.append(tmpt)

            yester_df.reset_index(inplace=True)
            today_df.reset_index(inplace=True)

            #dictionary_yester[i] = yester_df

        ## 구글 API로 데이터 올리기
            # 2주간의 데이터만 구글 스프레드 시트에 올리겠다.

          #  for k in range(3):
           #     sleep(1)
            #    gc2.append_row(yester_df.iloc[-1-k,:].values.tolist()+[i])




            dictionary_yester[i] = yester_df


    except :
        print('API 에러',i)
        error.append(i)



    sleep(3)

# dictionary_now['lis에서 정의했던 키워드 입력']
print(dictionary_now['토트넘'])