# visualization.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re

# Load data
df = pd.read_csv('komentar_sentimen.csv')

# 1. GRAFIK SENTIMEN
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Bar chart
sentiment_counts = df['sentimen'].value_counts()
colors = {'positif': 'green', 'netral': 'blue', 'negatif': 'red'}
bars = axes[0, 0].bar(sentiment_counts.index, sentiment_counts.values, 
                       color=[colors.get(x, 'gray') for x in sentiment_counts.index])
axes[0, 0].set_title('Distribusi Sentimen Komentar', fontsize=14)
axes[0, 0].set_xlabel('Sentimen')
axes[0, 0].set_ylabel('Jumlah Komentar')
for bar, count in zip(bars, sentiment_counts.values):
    axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                    str(count), ha='center', fontsize=10)

# Pie chart
axes[0, 1].pie(sentiment_counts.values, labels=sentiment_counts.index, 
               autopct='%1.1f%%', colors=['green', 'blue', 'red'])
axes[0, 1].set_title('Persentase Sentimen', fontsize=14)

# 2. AKTIVITAS WAKTU (Ekstrak tanggal dari waktu)
df['tanggal'] = pd.to_datetime(df['waktu'], format='%Y-%m-%d %H:%M:%S UTC', errors='coerce')
daily_comments = df.groupby(df['tanggal'].dt.date).size()
axes[1, 0].plot(daily_comments.index, daily_comments.values, marker='o', linestyle='-', color='purple')
axes[1, 0].set_title('Aktivitas Komentar per Hari', fontsize=14)
axes[1, 0].set_xlabel('Tanggal')
axes[1, 0].set_ylabel('Jumlah Komentar')
axes[1, 0].tick_params(axis='x', rotation=45)

# 3. Like per sentimen
like_by_sentiment = df.groupby('sentimen')['like'].mean()
axes[1, 1].bar(like_by_sentiment.index, like_by_sentiment.values, 
               color=[colors.get(x, 'gray') for x in like_by_sentiment.index])
axes[1, 1].set_title('Rata-rata Like per Sentimen', fontsize=14)
axes[1, 1].set_xlabel('Sentimen')
axes[1, 1].set_ylabel('Rata-rata Like')

plt.tight_layout()
plt.savefig('sentimen_analysis.png', dpi=150)
plt.show()
print("✅ Grafik tersimpan ke 'sentimen_analysis.png'")

# 4. WORDCLOUD per sentimen
def clean_for_wordcloud(text):
    text = re.sub(r'http\S+', '', str(text))
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower()

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for idx, sentimen in enumerate(['positif', 'netral', 'negatif']):
    # Gabungkan semua komentar dengan sentimen tertentu
    comments = df[df['sentimen'] == sentimen]['komentar'].fillna('').apply(clean_for_wordcloud)
    text = ' '.join(comments)
    
    if text.strip():
        wordcloud = WordCloud(width=400, height=400, 
                              background_color='white',
                              colormap='Greens' if sentimen == 'positif' else 
                                       'Blues' if sentimen == 'netral' else 'Reds',
                              max_words=100).generate(text)
        
        axes[idx].imshow(wordcloud, interpolation='bilinear')
        axes[idx].set_title(f'Wordcloud - Sentimen {sentimen.upper()}', fontsize=14)
        axes[idx].axis('off')
    else:
        axes[idx].text(0.5, 0.5, f'Tidak ada data\n{sentimen}', 
                       ha='center', va='center', fontsize=12)
        axes[idx].set_title(f'Sentimen {sentimen.upper()}')
        axes[idx].axis('off')

plt.tight_layout()
plt.savefig('wordcloud_sentimen.png', dpi=150)
plt.show()
print("✅ Wordcloud tersimpan ke 'wordcloud_sentimen.png'")