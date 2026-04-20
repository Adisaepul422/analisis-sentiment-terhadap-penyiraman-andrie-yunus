import pandas as pd
import re
import json          # <-- TAMBAHKAN INI
import nltk
from nltk.corpus import stopwords
import os

nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('indonesian'))

# Baca data dari Langkah 1
with open('tiktok_comments_7616677363820088584.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Flatten data
flattened_data = []
for comment in data:
    flattened_data.append({
        'komentar': comment.get('comment', ''),
        'like': comment.get('digg_count', 0),
        'waktu': comment.get('create_time')
    })
    for reply in comment.get('replies', []):
        flattened_data.append({
            'komentar': reply.get('comment', ''),
            'like': reply.get('digg_count', 0),
            'waktu': reply.get('create_time')
        })

df = pd.DataFrame(flattened_data)

# Bersihkan teks
def clean_text(text):
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r'http\S+', '', text)  # hapus link
    text = re.sub(r'@\w+', '', text)  # hapus mention
    text = re.sub(r'\[Sticker\].*', '', text)  # hapus sticker
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # hapus angka & simbol
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text.strip()

df['komentar_clean'] = df['komentar'].apply(clean_text)

# Hapus komentar kosong
df = df[df['komentar_clean'] != '']
print(f"✅ Data setelah cleaning: {len(df)} komentar")

# ============================================
# LABELING SENTIMEN (Berdasarkan kata kunci)
# ============================================

# Kata kunci POSITIF (dukungan, doa, semangat)
positif_keywords = [
    'semoga', 'aamiin', 'amin', 'sembuh', 'sehat', 'selamat', 'doa', 'doakan',
    'support', 'dukung', 'setuju', 'baik', 'lekas', 'pulih', 'kuat', 'sabar',
    'lindungi', 'Allah', 'Tuhan', 'Yesus', 'ampun', 'maaf', 'terima kasih',
    'keren', 'mantap', 'setuju', 'benar'
]

# Kata kunci NEGATIF (kritik, kemarahan, kecewa)
negatif_keywords = [
    'jahat', 'biadab', 'tega', 'sakit hati', 'marah', 'kesal', 'kecewa',
    'pemerintah', 'polisi', 'hukum', 'tidak adil', 'dzalim', 'zalim',
    'biadab', 'sampah', 'benci', 'kriminal', 'pelaku', 'dalang',
    'rezim', 'korup', 'mafia', 'beking', 'suruhan'
]

# Kata kunci NETRAL (informasi, pertanyaan, netral)
netral_keywords = [
    'apa', 'siapa', 'kenapa', 'bagaimana', 'dimana', 'kapan',
    'oh', 'noted', 'info', 'update', 'berita', 'kronologi'
]

def label_sentiment(text):
    text_lower = text.lower()
    
    # Cek positif
    for keyword in positif_keywords:
        if keyword in text_lower:
            return 'positif'
    
    # Cek negatif
    for keyword in negatif_keywords:
        if keyword in text_lower:
            return 'negatif'
    
    # Cek netral
    for keyword in netral_keywords:
        if keyword in text_lower:
            return 'netral'
    
    # Default
    return 'netral'

df['sentimen'] = df['komentar_clean'].apply(label_sentiment)

# Statistik sentimen
print("\n" + "="*50)
print("📊 STATISTIK SENTIMEN")
print("="*50)
sentiment_counts = df['sentimen'].value_counts()
for sentimen, count in sentiment_counts.items():
    percentage = (count / len(df)) * 100
    print(f"{sentimen.upper()}: {count} komentar ({percentage:.1f}%)")

# Simpan data yang sudah dilabel
df.to_csv('komentar_sentimen.csv', index=False)
df.to_excel('komentar_sentimen.xlsx', index=False)
print("\n✅ Data tersimpan ke 'komentar_sentimen.csv' dan 'komentar_sentimen.xlsx'")