import sys
[sys.path.append(i) for i in [".", ".."]]

import pandas as pd
from pandas import DataFrame
from datetime import datetime
import requests

# 순서 : 2
# 현재 시간 불러오는 함수
def _get_datetime_():
    now = datetime.now()
    now = now.strftime("%Y%m%d%H00")

    return now

# 순서 : 3
# parse to dataframe
def _parse_(response):
    lines = response.text.split("\n")

    datas = []
    for i in range(2, len(lines)-2):
        if i < 4: # Columns
            lines[i] = lines[i].replace("#", " ")
            lines[i] = lines[i].replace("-", " ")
        line = lines[i] + '\n'
        datas.append(line)

    with open("temp.csv", 'w') as f:
        for line in datas:
            f.write(line)

    df = pd.read_csv("temp.csv", sep="\s+")
    df = df.drop(index=0, axis=0)
    
    return df

# 순서 : 4
# 추출
def _extract_(df):
    columns_need = ['STN', 'TA', "RN", 'WS', 'WD', 'HM', "PV", 'TD', 'PA', 
                        "PS", "SS", 'SI', 'SD.2', 'CA', 'CA.1', 'CH', 'VS', 'TS', 'WW']
    df = df[columns_need]

    # 컬럼명 변경 - 테이블에 맞춰서
    real_cols = ['STN', 'ta', "rn", 'ws', 'wd', 'hm', "pv", 'td', 
                    'pa', "ps", "ss", 'icsr', 'dsnw', 'dc10Tca', 'dc10LmcsCa', 
                    'lcsCh', 'vs', 'ts', 'WW']
    df.columns = real_cols

    # 컬럼명 포맷팅 ("WW" 빼고)
    names = {'102': 'bangryeong_0', '112': 'incheon_1', '201': 'ganghwado_2', 
                '203': 'icheon_3', '99' : 'paju_4', '98' : 'dongducheon_5', 
                '119' : 'suwon_6', '202' : 'yangpyeong_7', '108' : 'seoul_8'}

    all_df = pd.DataFrame()

    for idx, item in df.iterrows():
        temp_df = pd.DataFrame(item).T
        
        # 인덱스 없애서 한줄로 맞추기 위해
        temp_df.reset_index(drop=True, inplace=True)
        
        # WW를 꺼내서 원핫인코딩(프리픽스는 x0)
        dummy = pd.get_dummies(temp_df["WW"], prefix = "x0")
        
        # WW를 가져가 썼으니까 삭제(temp_df -> 한줄을 데이터프레임화 시킨거)
        temp_df.drop("WW", axis=1, inplace=True)
        
        # WW를 제거한 기존 데이터프레임에 원핫인코딩된 데이터프레임을 합쳐주는 작업
        temp_df = pd.concat([temp_df, dummy], axis=1)
        
        # 새로 바뀐 컬럼명 보관
        new_cols = []
        
        for col in temp_df.keys():
            if col in ["STN"]:
                continue
            
            tag = item.get("STN", None)
            if tag in names:
                comp_key = col + "_" + names[str(tag)]
                new_cols.append(comp_key)
        
        if len(new_cols) > 0:
            # new_cols.append(dummy.columns)
            temp_df.drop("STN", axis=1, inplace=True)
            temp_df.columns = new_cols
            
            all_df = pd.concat([all_df, temp_df], axis=1)
    return all_df

# 순서 : 1
# 기상청 지역별 호출
def get_weather() -> DataFrame : # "암묵적!!" 형태 지정 주석 (강제하진 않음)
    url = f"https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php?tm={_get_datetime_()}&authKey=jvwEqhhGTIW8BKoYRhyFkQ&dataType=JSON"
    response = requests.get(url)
    df = _parse_(response)
    df = _extract_(df)
    return df
