import pandas as pd

# 데이터 파일 불러오기
df_festivals = pd.read_csv("festivalDT.csv")

# '축제 유형'을 기반으로 목표 변수 컬럼 생성
df_festivals['목표 변수'] = df_festivals['축제 유형']  # '축제 유형' 컬럼을 '목표 변수'로 복사

# 데이터 파일 저장 (새로운 컬럼이 추가됨)
df_festivals.to_csv("festivalDT_with_target.csv", index=False)
