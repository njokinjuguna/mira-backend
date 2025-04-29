import re
from nltk import ngrams

def extract_keywords(query: str) -> list:
    """
    Cleans and extracts important keywords and phrases from a user's query.
    Removes stopwords and unnecessary noise like punctuation.
    """
    stopwords = set([
        "hi", "hello", "hey", "please", "kindly", "give", "can", "could", "would",
        "you", "your", "me", "the", "find", "get", "have", "got", "want", "that", "of", "for",
        "mira", "mirror", "area"
    ])

    # 🧹 Lowercase the query
    query = query.lower()

    # 🧹 Remove punctuation (keep only letters, numbers, spaces)
    query = re.sub(r"[^a-zA-Z0-9\s]", "", query)

    # 🧹 Split into words
    words = query.split()

    # 🧹 Generate n-grams (2-word phrases)
    n_grams = [" ".join(ngram) for ngram in ngrams(words, 2)]

    # 🧹 Combine single words and n-grams, then remove stopwords
    keywords = [word for word in words + n_grams if word not in stopwords]

    return keywords