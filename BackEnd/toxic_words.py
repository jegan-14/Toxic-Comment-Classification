import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# Load Jigsaw dataset
df = pd.read_csv("data.csv")

# Split comments into toxic and non-toxic
toxic_comments = df[df[df.columns[2:]].sum(axis=1) > 0]["comment_text"]
safe_comments = df[df[df.columns[2:]].sum(axis=1) == 0]["comment_text"]

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_toxic = vectorizer.fit_transform(toxic_comments)
tfidf_safe = vectorizer.transform(safe_comments)

# Compute mean TF-IDF scores for each word
toxic_tfidf_scores = tfidf_toxic.mean(axis=0).A1
safe_tfidf_scores = tfidf_safe.mean(axis=0).A1

# Get feature names (words)
words = vectorizer.get_feature_names_out()

# Find words that have higher TF-IDF in toxic comments
toxic_word_scores = {
    word: toxic_tfidf_scores[i] - safe_tfidf_scores[i] for i, word in enumerate(words)
}
# Adjust the threshold to include more words
toxic_words = [
    word for word, score in toxic_word_scores.items() if score > 0.001
]  # Lower threshold
# Threshold

# Save dataset
toxic_df = pd.DataFrame({"word": toxic_words, "label": 1})
safe_words = list(set(words) - set(toxic_words))
safe_df = pd.DataFrame({"word": safe_words, "label": 0})

final_df = pd.concat([toxic_df, safe_df])
final_df.to_csv("toxic_words_tfidf.csv", index=False)

print("Dataset saved with", len(final_df), "words!")
