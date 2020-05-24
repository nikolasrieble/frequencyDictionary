import json
from pathlib import Path

from nltk import FreqDist
from nltk.tokenize import word_tokenize, sent_tokenize

from utils.get_connection import get_mydb

current_path = Path.cwd()
data_path = current_path.parent / 'data'

if __name__ == '__main__':
    mydb = get_mydb()
    res = dict()
    all_languages = ['de', 'tr']
    for language in all_languages:
        this_collection = mydb[language]

        all_headlines = []
        all_articles = []

        for entry in this_collection.find():
            all_headlines.append(entry.get('headline'))
            all_articles.append(entry.get('text'))

        n_articles = len(all_articles)
        n_sentences = 0
        n_words = 0
        all_words = []

        for this_article in all_articles:
            these_words = word_tokenize(this_article)
            these_sentences = sent_tokenize(this_article)

            these_words = [w for w in these_words if w.isalpha()]

            all_words += these_words
            n_words += len(these_words)
            n_sentences += len(these_sentences)

        avg_sentences_per_article = n_sentences / n_articles
        avg_words_per_sentence = n_words / n_sentences
        avg_words_per_article = n_words / n_articles

        word_freq = FreqDist(all_words)
        most_common = word_freq.most_common(5)
        most_common = {k: v for k, v in most_common}

        stat = dict(
            language=language,
            most_common=most_common,
            n_articles=n_articles,
            n_sentences=n_sentences,
            n_words=n_words,
            avg_sentences_per_article=round(avg_sentences_per_article, 2),
            avg_words_per_article=round(avg_words_per_article, 2),
            avg_words_per_sentence=round(avg_words_per_sentence, 2),
        )

        res.update({language: stat})

    with open(str(data_path / 'res.json'), 'w') as stat:
        json.dump(res, stat)
