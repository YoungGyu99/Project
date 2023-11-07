# pip install python-Levenshtein
from flask import Flask, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from fuzzywuzzy import fuzz

app = Flask(__name__)

# Load festival data
festival_data = pd.read_csv("festivalDT.csv")

# Festival data: Select important columns
festival_data = festival_data[['FCLTY_NM', 'FSTVL_CN', 'OPMTN_PLACE_NM', 'FSTVL_BEGIN_DE', 'FSTVL_END_DE', 'HMPG_ADDR']]

# Handle missing values
festival_data = festival_data.dropna()

# TF-IDF vectorization for festival content
tfidf_vectorizer_content = TfidfVectorizer()
tfidf_matrix_content = tfidf_vectorizer_content.fit_transform(festival_data['FSTVL_CN'])

# Compute cosine similarity for festival content
cosine_sim_content = linear_kernel(tfidf_matrix_content, tfidf_matrix_content)

# Set a lower similarity threshold (20%)
similarity_threshold = 20

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
    except:
        pass
    return date_string

def recommend_similar_festivals(user_preference, num_recommendations=10):
    user_preference = user_preference.lower()
    festival_scores = []

    for idx, festival_content in enumerate(festival_data['FSTVL_CN']):
        similarity_score = fuzz.ratio(user_preference, festival_content.lower())
        if similarity_score >= similarity_threshold:
            festival_scores.append((idx, similarity_score))

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
            'Website': festival_data['HMPG_ADDR'].iloc[idx]
        }
        recommendations.append(recommendation_info)

    return recommendations

@app.route('/', methods=['GET', 'POST'])
def chat():
    user_preference = ""
    recommendations = []

    if request.method == 'POST':
        user_preference = request.form.get('user_preference', '')  # 빈 문자열을 기본값으로 설정
        recommendations = recommend_similar_festivals(user_preference)

    return render_template('chat.html', user_preference=user_preference, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
