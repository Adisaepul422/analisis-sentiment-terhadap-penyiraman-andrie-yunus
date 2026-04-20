# lstm_model.py
import pandas as pd
import numpy as np
import os
import pickle
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

print("="*50)
print("SENTIMENT ANALYSIS (Logistic Regression)")
print("="*50)

# ============================================
# ⚠️ PERHATIKAN: Sesuaikan path ini!
# ============================================

# Opsi 1: Jika file di C:\Data\output\
INPUT_PATH = r'C:\Data\output\komentar_sentimen.csv'

# Opsi 2: Jika file di C:\Data\ (satu folder dengan script)
# INPUT_PATH = r'C:\Data\komentar_sentimen.csv'

# Opsi 3: Cari otomatis di folder yang sama dengan script
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# INPUT_PATH = os.path.join(SCRIPT_DIR, 'komentar_sentimen.csv')

MODEL_PATH = r'C:\Data\output\sentiment_model_lr.pkl'

# ============================================

# Cek apakah file ada
if not os.path.exists(INPUT_PATH):
    print(f"\n❌ ERROR: File tidak ditemukan!")
    print(f"   Dicari di: {INPUT_PATH}")
    print(f"\n📌 Solusi:")
    print(f"   1. Pastikan file komentar_sentimen.csv sudah ada")
    print(f"   2. Jalankan script preprocessing terlebih dahulu")
    print(f"   3. Atau sesuaikan path INPUT_PATH di script")
    exit()

print(f"\n📁 Membaca file: {INPUT_PATH}")

# Load data
df = pd.read_csv(INPUT_PATH)
df = df.dropna(subset=['komentar_clean'])
df = df[df['komentar_clean'].str.strip() != '']
print(f"✅ Data: {len(df)} komentar")

# Encode label
le = LabelEncoder()
y = le.fit_transform(df['sentimen'])

# Vectorize
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df['komentar_clean'])

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\n✅ TEST ACCURACY: {acc:.4f} ({acc*100:.2f}%)")
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# Buat folder output jika belum ada
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# Save
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model, f)
with open(r'C:\Data\output\vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
with open(r'C:\Data\output\label_encoder_lr.pkl', 'wb') as f:
    pickle.dump(le, f)

print(f"\n💾 Model saved: {MODEL_PATH}")

# Test
test_texts = ["semoga cepat sembuh", "pemerintah jahat", "info saja"]
X_test_vec = vectorizer.transform(test_texts)
preds = model.predict(X_test_vec)
print("\n🔮 Test:")
for text, pred in zip(test_texts, preds):
    print(f"   '{text}' → {le.inverse_transform([pred])[0]}")

print("\n✅ Selesai!")