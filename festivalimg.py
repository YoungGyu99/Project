from googlesearch import search

# 축제 이름 리스트 (이 부분을 원하는 축제 이름으로 변경하세요)
festival_names = ['축제1', '축제2', '축제3']





# URL을 저장할 텍스트 파일을 열고 URL을 기록합니다.
with open('festival_poster_urls.txt', 'w') as file:
    for festival_name in festival_names:
        # 검색어 구성
        query = f"{festival_name} 축제 포스터"

        # Google 검색을 통해 이미지 검색 결과 페이지 URL 가져오기
        search_results = search(query, num=1, stop=1)

        for result in search_results:
            # URL을 파일에 기록
            file.write(f"{festival_name}: {result}\n")

print("URL 저장이 완료되었습니다.")
