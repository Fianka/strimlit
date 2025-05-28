import streamlit as st
from pymongo import MongoClient
import plotly.graph_objs as go
from collections import Counter
import re

# Gunakan koneksi MongoDB Atlas dari secrets
client = MongoClient(st.secrets["mongo"]["uri"])
db = client.flo_health
collection = db.articles

# Ambil data artikel
articles = list(collection.find())

st.title("Visualisasi Artikel Flo Health")

# 1. Visualisasi Artikel tentang Menstruasi
menstruation_keywords = ["menstruation", "period", "menstrual", "dysmenorrhea", "cramps", "cycle"]
menstruation_count = sum(
    any(keyword in (article['title'] + " " + article['content']).lower() for keyword in menstruation_keywords)
    for article in articles
)

menstruation_pie = go.Figure(data=[go.Pie(
    labels=['Menstruation Related', 'Others'],
    values=[menstruation_count, len(articles) - menstruation_count],
    hole=0.4
)])
menstruation_pie.update_layout(title="Proporsi Artikel yang Membahas Menstruasi")

st.plotly_chart(menstruation_pie)

# 2. Kata Kunci Sering di Judul
title_words = []
for article in articles:
    title_words += re.findall(r'\b\w+\b', article['title'].lower())

stopwords = set(['the', 'and', 'of', 'to', 'in', 'a', 'is', 'for', 'on', 'with', 'your', 'you', 'how', 'what', 'why', 'are'])
filtered_words = [w for w in title_words if w not in stopwords and len(w) > 2]
word_counts = Counter(filtered_words)
most_common = word_counts.most_common(10)

common_bar = go.Figure([go.Bar(x=[w[0] for w in most_common], y=[w[1] for w in most_common])])
common_bar.update_layout(title="Top 10 Kata Kunci Paling Sering Muncul di Judul", xaxis_title="Kata", yaxis_title="Frekuensi")

st.plotly_chart(common_bar)

# 3. Kata Kunci Paling Jarang 
least_common = [word for word, count in word_counts.items() if count == 1]
least_common_limited = least_common[:10]

rare_bar = go.Figure([go.Bar(x=least_common_limited, y=[1]*len(least_common_limited))])
rare_bar.update_layout(title="Top 10 Kata Kunci Paling Jarang Muncul di Judul", xaxis_title="Kata", yaxis_title="Frekuensi")

st.plotly_chart(rare_bar)
