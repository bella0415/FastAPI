# import logging
# from sqlalchemy.orm import Session
# from database.db_config import SessionLocal, engine
# from typing import List
# from fastapi import Depends, FastAPI, HTTPException

# logging.basicConfig()  # 쿼리 로그를 남기기

# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO) 

# app = FastAPI()

# def get_db() :
#     db = SessionLocal()
    
#     try : 
#         yield db # 비동기 프로그래밍 
        
#     finally :
#         db.close() # db닫음
        
# @app.get("/")
# def hello() :
#     return {"message" : "hello"}

from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
# CORSMiddleware 을 사용하여 FastAPI 응용 프로그램의 교차 출처 리소스 공유 환경을 설정할 수 있음
app = FastAPI()

origins = ['http://172.31.39.223/']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"Hello": "World"}
