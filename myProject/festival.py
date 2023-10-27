from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from fuzzywuzzy import fuzz

app = Flask(__name__)

# 축제 데이터 로드
festival_data = pd.read_csv("festivalDT.csv")

# 검색 키워드 데이터 로드 (DM_FSTVL_TOP10_TREND_DATA_RESULT_20231025.csv)
search_volume_data = pd.read_csv("DM_FSTVL_TOP10_TREND_DATA_RESULT_20231025.csv", encoding="utf-8")

# Festival data: Select important columns
festival_data = festival_data[['FCLTY_NM', 'FSTVL_CN', 'OPMTN_PLACE_NM', 'FSTVL_BEGIN_DE', 'FSTVL_END_DE', 'HMPG_ADDR', 'CTPRVN_NM', 'SIGNGU_NM']]

# Handle missing values
festival_data = festival_data.dropna()

# TF-IDF vectorization for festival content
tfidf_vectorizer_content = TfidfVectorizer()
tfidf_matrix_content = tfidf_vectorizer_content.fit_transform(festival_data['FSTVL_CN'])

# Compute cosine similarity for festival content
cosine_sim_content = linear_kernel(tfidf_matrix_content, tfidf_matrix_content)

# Set a lower similarity threshold (20%)
similarity_threshold = 20

search_cache = []  # 검색어 캐시

# Define a function to convert date to the desired format
def convert_date_to_month(date_string):
    try:
        date_parts = date_string.split('-')
        if len(date_parts) == 3:
            day = int(date_parts[2])
            if 1 <= day <= 10:
                return f"{date_parts[1]}월 초"
            elif 11 <= day <= 20:
                return f"{date_parts[1]}월 중순"
            elif 21 <= day <= 31:
                return f"{date_parts[1]}월 말"
    except Exception as e:
        pass
    return date_string

def recommend_similar_festivals(user_preference, num_recommendations=10):
    user_preference = user_preference.lower()
    festival_scores = []

    for idx, festival_content in enumerate(festival_data['FSTVL_CN']):
        similarity_score = fuzz.ratio(user_preference, festival_content.lower())
        if similarity_score >= similarity_threshold:
            festival_scores.append((idx, similarity_score))

    # Check for location matches
    location_preference = user_preference
    for idx, location in enumerate(festival_data['OPMTN_PLACE_NM']):
        if location_preference.lower() in location.lower():
            festival_scores.append((idx, 100))  # Assign a high score for exact location matches

    festival_scores = sorted(festival_scores, key=lambda x: x[1], reverse=True)
    top_similar_festivals = festival_scores[:num_recommendations]

    recommendations = []
    for idx, _ in top_similar_festivals:
        recommendation_info = {
            'Name': festival_data['FCLTY_NM'].iloc[idx],
            'Content': festival_data['FSTVL_CN'].iloc[idx],
            'Location': festival_data['OPMTN_PLACE_NM'].iloc[idx],
            'Start Date': convert_date_to_month(festival_data['FSTVL_BEGIN_DE'].iloc[idx]),
            'End Date': convert_date_to_month(festival_data['FSTVL_END_DE'].iloc[idx]),
            'Website': festival_data['HMPG_ADDR'].iloc[idx],
            'Region': f"{festival_data['CTPRVN_NM'].iloc[idx]} {festival_data['SIGNGU_NM'].iloc[idx]}"
        }
        recommendations.append(recommendation_info)

    return recommendations

def update_search_rankings():
    global search_cache
    search_cache = [search.lower() for search in search_cache]  # 모든 검색어를 소문자로 변경
    search_rankings = {search: search_cache.count(search) for search in search_cache}  # 각 검색어의 빈도수를 계산

    # 빈도수 순으로 정렬하고 중복을 없애고 순위를 다시 지정
    unique_search_rankings = list(set(search_cache))
    unique_search_rankings = sorted(unique_search_rankings, key=lambda x: search_rankings[x], reverse=True)
    unique_search_rankings = [(i + 1, keyword) for i, keyword in enumerate(unique_search_rankings[:10])]

    return unique_search_rankings

@app.route('/', methods=['GET', 'POST'])
def chat():
    global search_cache
    user_preference = ""
    recommendations = []

    # 상위 검색 키워드를 가져옵니다.
    top_search_rankings = update_search_rankings()

    if request.method == 'POST':
        user_preference = request.form.get('user_preference', '')  # 기본값으로 빈 문자열을 설정합니다
        recommendations = recommend_similar_festivals(user_preference)
        search_cache.append(user_preference)  # 검색 캐시 업데이트

    return render_template('chat.html', user_preference=user_preference, recommendations=recommendations,
                           top_search_rankings=top_search_rankings)

@app.route('/home')
def home():
    # 홈 화면을 렌더링합니다.
    return render_template('home.html')  # 'home.html'은 처음 화면을 나타내는 템플릿 파일명

@app.route('/go_to_chat')
def go_to_chat():
    # "축제봇" 화면으로 이동합니다.
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True)
