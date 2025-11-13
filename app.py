from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib, json, os
from train_phish_model import extract_features_from_url

app = Flask(__name__)
CORS(app)

MODEL_PATH = 'models/phish_model.joblib'
FEAT_JSON = 'models/feature_columns.json'

if not os.path.exists(MODEL_PATH):
    raise SystemExit("Model not found. Run: python train_phish_model.py")

model = joblib.load(MODEL_PATH)
with open(FEAT_JSON) as f:
    FEATURE_COLS = json.load(f)

@app.route('/')
def home():
    return send_file('frontend/index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    url = (data.get('url') or '').strip()
    if not url:
        return jsonify({'error': 'url required'}), 400

    feats = extract_features_from_url(url)
    X = [feats.get(c, 0) for c in FEATURE_COLS]
    proba = float(model.predict_proba([X])[0][1])
    label = int(proba >= 0.5)
    explanation = []
    if feats.get('has_ip'): explanation.append('Uses IP address')
    if feats.get('suspicious_keyword'): explanation.append('Suspicious keyword')
    if feats.get('subdomain_count', 0) >= 2: explanation.append('Several subdomains')
    if feats.get('url_length', 0) > 100: explanation.append('Very long URL')

    return jsonify({
        'url': url,
        'phishing_probability': proba,
        'label': label,
        'explanation': explanation
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
