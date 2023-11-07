import pandas as pd

# CSV 파일 불러오기 (CSV 파일 경로를 변경하십시오)
df_festivals = pd.read_csv("festivalDT.csv")

# 사용자 입력에 해당하는 축제 정보를 검색하는 함수
def get_similar_festival_info(title):
    # 입력한 텍스트가 축제 이름과 부분적으로 일치하는지 확인
    festival_info = df_festivals[df_festivals['FCLTY_NM'].str.contains(title, case=False)]
    return festival_info

while True:
    text = input("축제 이름을 입력하세요 (관련된 콘텐츠를 찾을 수 있도록 부분 일치): ")
    festival_info = get_similar_festival_info(text)

    if not festival_info.empty:
        # 이름, 날짜, 개최지역, 행사 정보 및 링크 정보 출력
        for index, row in festival_info.iterrows():
            print("축제 이름:", row['FCLTY_NM'])
            print("개최 날짜:", row['FSTVL_BEGIN_DE'], "-", row['FSTVL_END_DE'])
            location = f"{row['CTPRVN_NM']} {row['SIGNGU_NM']}"
            location = location.replace('nan', 'Unknown')  # 'nan'을 'Unknown'으로 대체
            print("개최 지역:", location)
            print("행사 정보:", row['FSTVL_CN'])
            print("축제 링크:", row['HMPG_ADDR'])
            print("-" * 30)
    else:
        print("해당하는 관련된 축제를 찾을 수 없습니다.")
