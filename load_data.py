# load_data.py
import json
import pandas as pd
import re
from datetime import datetime

# Baca file JSON hasil scraping
with open('tiktok_comments_7616677363820088584.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ Jumlah komentar utama: {len(data)}")

# Hitung total komentar termasuk balasan
total_comments = len(data)
total_replies = sum(len(comment.get('replies', [])) for comment in data)
print(f"✅ Jumlah balasan (replies): {total_replies}")
print(f"✅ TOTAL DATA: {total_comments + total_replies} komentar")

# Flatten data untuk mudah diproses
flattened_data = []

for comment in data:
    # Komentar utama
    flattened_data.append({
        'id': comment.get('cid'),
        'username': comment.get('username'),
        'nickname': comment.get('nickname'),
        'komentar': comment.get('comment', ''),
        'waktu': comment.get('create_time'),
        'like': comment.get('digg_count', 0),
        'tipe': 'utama',
        'parent_id': None
    })
    
    # Balasan komentar
    for reply in comment.get('replies', []):
        flattened_data.append({
            'id': reply.get('cid'),
            'username': reply.get('username'),
            'nickname': reply.get('nickname'),
            'komentar': reply.get('comment', ''),
            'waktu': reply.get('create_time'),
            'like': reply.get('digg_count', 0),
            'tipe': 'balasan',
            'parent_id': comment.get('cid')
        })

# Buat DataFrame
df = pd.DataFrame(flattened_data)
print(f"\n📊 DataFrame shape: {df.shape}")
print(df.head())