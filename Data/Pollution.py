import sys
[sys.path.append(i) for i in [".", ".."]]


import pandas as pd
import numpy as np
import requests

# 
# pollution API 호출
def get_pollution() :
    
    # API 호출
    ##########################
    key = 'BVQCCUgpx/b8HvRWaOf+lXv7wzOcIMh6bXw/JyBoqDbstzhj6bDJhPY7UW+H296mK5kLc/jmUs4+kpuAUA7t+g=='
    url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty'
        
    params ={
        'serviceKey' : key, 
        'returnType' : 'json', 
        'numOfRows' : 10000, 
        'sidoName' : "전국",
        }
    
    res = requests.get(url, params=params)
    result = res.json()
    ##########################



    # 방어코드
    # 비어 있다면 Exception !
    ##########################
    response = result.get("response", None)
    if response is None: 
        raise Exception("Response가 비어있음")

    body = response.get("body", None)
    if body is None: 
        raise Exception("Body가 비어있음")

    total_count = body.get("totalCount", None)
    if total_count is None: 
        raise Exception("가져온 아이템수가 0임")

    items = body.get("items", None)
    if items is None: 
        raise Exception("아이템이 한개도 없음")
    ##########################


    # API 데이터를 필요한 부분만 발췌 및 정제
    ##########################
    pollution_all = {}
    for item in items:
        station = "NULL"
        poll = {}
        for key, value in item.items():
            
            if key == "stationName":
                station = value
                
            if key == "so2Value" : poll["SO2"] = value
            if key == "coValue"  : poll["CO"] = value
            if key == "pm10Value": poll["PM10"] = value
            if key == "no2Value" : poll["NO2"] = value
            if key == "o3Value"  : poll["O3"] = value
                
            
        pollution_all[station] = poll
    ##########################
    
    
    # 컬럼명 정리및 부분 저장
    ##########################
    # 별칭 담겨있는 텍스트 파일 읽어오기
    with open("station_alias_dic.txt", "r", encoding = "utf-8") as f:
        name_tags = f.readlines()
    
    # 모두 모을 데이터 프레임 생성
    all_df = pd.DataFrame()
    
    for station, pollution in pollution_all.items():
        
        # 측정소명의 별칭 가져오기
        station_nametag = None
        for tag in name_tags:
            tag = tag.strip()
            # : 를 기준으로 key,value 나눔
            key, value = tag.split(":")
            
            if station == key:
                station_nametag = value
                
        
        # 네임태그가 존재한다면(내가 선정한 컬럼이라면)
        if station_nametag is not None:
            df_temp = pd.DataFrame(pollution, index = [0])
            
            # 컬럼명 변경
            cols = [k+station_nametag for k in pollution.keys()]
            df_temp.columns = cols
            
            # 중복찾기
            # 교집합 intersection 이용
            exist_cols = list(set(all_df.columns).intersection(cols))
            
            # 중복이 한개도 없으면
            if len(exist_cols) == 0:
                all_df = pd.concat([all_df, df_temp], axis = 1)
    
    return all_df
