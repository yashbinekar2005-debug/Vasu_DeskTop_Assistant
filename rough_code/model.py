import re
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_qa_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        dataset = []
        for line in lines:
            if ':' in line:
                q, a = line.split(':', 1)
                dataset.append({
                    'question': q.strip(),
                    'answer': a.strip()
                })
    return dataset

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    tokens = word_tokenize(text.lower())
    tokens = [ps.stem(t) for t in tokens if t.isalnum() and t not in stop_words]
    return ' '.join(tokens)

def train_vectorizer(dataset):
    corpus = [preprocess_text(qa['question']) for qa in dataset]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    return vectorizer, X

def get_answer(question, vectorizer, X, dataset, threshold=0.25):
    question = preprocess_text(question)
    q_vec = vectorizer.transform([question])
    similarity = cosine_similarity(q_vec, X)

    best_idx = similarity.argmax()
    best_score = similarity[0][best_idx]

    if best_score < threshold:
        return None

    return dataset[best_idx]['answer']
