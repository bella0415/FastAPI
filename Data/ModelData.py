import sys
[sys.path.append(i) for i in [".", ".."]]

import pandas as pd
from Weather import get_weather
from Pollution import get_pollution
from datetime import datetime
import pickle
import joblib

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, ExtraTreesRegressor, StackingClassifier
from xgboost import XGBClassifier

# 모든 순서는 시작점 기준 ex. 5,6

# 순서 : 4
# weather,pollution concat 함수
# model e
def concat(weather, pollution):
    all_df = pd.concat([weather, pollution], axis=1)
    
    # 모델의 피처들이 있는 텍스트파일 열어줌
    with open("model_features.txt", "r") as f:
        used_cols = []
        for line in f.readlines():
            used_cols.append(line.replace("\n", "").strip())
    
    # model과 피처를 동일하게 해줌
    # col = model feature 한 개씩
    # col이 all_df에 없다면 -> col_df로 새로 생성
    # col 명에 lcsCh,x0이 포함 되어 있다면 기존의 all_df와 새로 만들어준 col_df를 concat
    for col in used_cols:
        if col not in all_df:
            col_df = pd.DataFrame({col:[0]})
            if "lcsCh" in col:
                all_df = pd.concat([all_df, col_df], axis=1)
            if "x0" in col:
                all_df = pd.concat([all_df, col_df], axis=1)
    
    # col = all_df 컬럼 한 개씩
    # all_df안에 있는 col이 model_features에 없다면
    # all_df에 있는 col 버림
    # 한줄 : model_features에 없는 col은 all_df에서 drop
    for col in all_df:
        if col not in used_cols:
            all_df.drop(col, axis=1, inplace=True)
            
    return all_df

# 순서 : 3
# wether,pollution 각 변수에 데이터들을 load 한 후, concat함수 호출!
def load_data():
    weather = get_weather()
    pollution = get_pollution()
    
    df = concat(weather, pollution)

    return fillna(df)

# 순서 : 6
# 결측치 처리할 평균 데이터 가져옴
def mean_data():
    with open('pickle/mean.pkl', 'rb') as f:
        mean = pickle.load(f)
    return mean

# 순서 : 5
# 결측치 처리 
# 결측치가 있으면 mean.pkl 데이터로 대체
def fillna(df):
    mean = mean_data()
    mean.set_index("monthtime", inplace=True)

    now_datetime = datetime.now().strftime("%m-%d %H:00:00")

    for col in df.columns:
        if df[col].values.tolist().pop() == "-":
            df[col] = df[col].replace("-", mean.loc[now_datetime, col])

    with open("model_features.txt", "r") as f:
            used_cols = []
            for line in f.readlines():
                used_cols.append(line.replace("\n", "").strip())

    df = df[used_cols]
    df = df.astype(float)

    return df

# 순서 : 2
# 모델 불러오기
def model():
    model = joblib.load('./pickle/final_stacking_model.pkl')
    return model

# test용 이랄까,,
# predict가 숫자로 반환
def predict(): 
    return model().predict(load_data())

# predict 한글로 반환
# 순서 : 1
def predict_word():
    replace_word = {
        0 : "좋음",
        1 : "보통",
        2 : "나쁨",
        3 : "아주나쁨"
    }
    # predict 할 때, model 엔지니어가 정한 피처들과 동일 해야함 (이 역할을 해주는게 concat함수)
    pred = model().predict(load_data()).tolist().pop()
    return replace_word[pred]