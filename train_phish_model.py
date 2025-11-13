import pandas as pd
import re, json, joblib, os
from urllib.parse import urlparse
import tldextract
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

def extract_features_from_url(url):
    feats = {}
    feats['url_length'] = len(url)
    feats['has_ip'] = bool(re.search(r'(\d{1,3}\.){3}\d{1,3}', url))
    feats['num_dots'] = url.count('.')
    feats['num_hyphens'] = url.count('-')
    feats['num_at'] = url.count('@')
    feats['num_question'] = url.count('?')
    feats['num_equal'] = url.count('=')
    feats['subdomain_count'] = len(tldextract.extract(url).subdomain.split('.')) if tldextract.extract(url).subdomain else 0
    suspicious_keywords = ['login', 'secure', 'account', 'update', 'free', 'verify', 'bank', 'confirm', 'signin']
    feats['suspicious_keyword'] = any(kw in url.lower() for kw in suspicious_keywords)
    return feats

def load_or_create_dataset():
    os.makedirs('data', exist_ok=True)
    path = 'data/sample_urls.csv'
    if os.path.exists(path):
        df = pd.read_csv(path)
    else:
        # Create sample data
        urls = [
            ('https://www.google.com', 0),
            ('https://secure-login.paypal.com', 1),
            ('https://accounts.google.com', 0),
            ('http://192.168.0.1/login', 1),
            ('http://update-bank-info.com', 1),
            ('https://github.com', 0),
            ('https://verify-facebook.com', 1),
            ('https://microsoft.com', 0),
        ]
        df = pd.DataFrame(urls, columns=['url', 'label'])
        df.to_csv(path, index=False)
    return df

def main():
    df = pd.read_csv('data/urls_fixed.csv', encoding='latin1', on_bad_lines='skip', engine='python')


    feats = df['url'].apply(extract_features_from_url).apply(pd.Series)
    feats['label'] = df['label']
    X = feats.drop(columns=['label'])
    y = feats['label']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)
    print("ROC-AUC:", round(auc, 3))

    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/phish_model.joblib')
    json.dump(list(X.columns), open('models/feature_columns.json', 'w'))
    print("✅ Model saved successfully!")

if __name__ == '__main__':
    main()
