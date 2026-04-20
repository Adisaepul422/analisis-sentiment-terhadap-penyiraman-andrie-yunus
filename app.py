# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import pickle
import os

app = Flask(__name__)
CORS(app)

# ============================================
# PATH FILE
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, 'output', 'sentiment_model_lr.pkl')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'output', 'vectorizer.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'output', 'label_encoder_lr.pkl')
DATA_PATH = os.path.join(BASE_DIR, 'output', 'komentar_sentimen.csv')

print("="*50)
print("🚀 STARTING BACKEND API")
print("="*50)

# ============================================
# LOAD MODEL
# ============================================
if not os.path.exists(MODEL_PATH):
    print(f"❌ Model not found. Run lstm_model.py first!")
    MODEL_AVAILABLE = False
else:
    MODEL_AVAILABLE = True
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(ENCODER_PATH, 'rb') as f:
        label_encoder = pickle.load(f)
    print(f"✅ Model loaded")

# ============================================
# LOAD DATA
# ============================================
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    print(f"✅ Data loaded: {len(df)} komentar")
else:
    df = pd.DataFrame()
    print(f"⚠️ Data not found")

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Tampilkan dashboard"""
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    if df.empty:
        return jsonify({'error': 'No data'}), 500
    
    sentiment_counts = df['sentimen'].value_counts()
    return jsonify({
        'total': len(df),
        'positif': int(sentiment_counts.get('positif', 0)),
        'netral': int(sentiment_counts.get('netral', 0)),
        'negatif': int(sentiment_counts.get('negatif', 0))
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    if not MODEL_AVAILABLE:
        return jsonify({'error': 'Model not available'}), 500
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Text required'}), 400
    
    X = vectorizer.transform([text])
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    
    sentiment = label_encoder.inverse_transform([pred])[0]
    
    return jsonify({
        'text': text,
        'sentiment': sentiment,
        'confidence': float(max(proba))
    })

@app.route('/api/comments', methods=['GET'])
def get_comments():
    if df.empty:
        return jsonify({'error': 'No data'}), 500
    
    limit = request.args.get('limit', 30, type=int)
    comments = df[['komentar', 'sentimen', 'like']].head(limit).to_dict('records')
    
    return jsonify({'comments': comments})

@app.route('/api/sentiment_distribution', methods=['GET'])
def get_distribution():
    if df.empty:
        return jsonify({'error': 'No data'}), 500
    
    sentiment_counts = df['sentimen'].value_counts()
    return jsonify({
        'labels': sentiment_counts.index.tolist(),
        'values': sentiment_counts.values.tolist()
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': MODEL_AVAILABLE,
        'data_loaded': not df.empty
    })

# ============================================
# RUN SERVER
# ============================================
if __name__ == '__main__':
    print("\n" + "="*50)
    print("✅ Server running at: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)