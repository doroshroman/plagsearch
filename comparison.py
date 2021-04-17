#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import textract
import nltk
import re
import pymorphy2
from num2words import num2words
import string
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import functools

try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt')


morph = pymorphy2.MorphAnalyzer(lang='uk')


def tokenize(text, stop_words, lang='uk') -> List[str]:
    tokenized_list = []
    sentences = nltk.sent_tokenize(text)

    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        digits_to_words = [
            num2words(
                word,
                lang=lang) if word.isdigit() else word for word in words]
        words_lower = [word.lower() for word in digits_to_words]
        words_without_stop = [
            word for word in words_lower if word not in stop_words]

        for token in words_without_stop:
            parsed = morph.parse(token)[0]
            tokenized_list.append(parsed.normal_form)

    return tokenized_list


def normalize(text, stop_words, lang='uk') -> List[str]:
    """Remove  punctuation, multiple new line, 
       Return tokenized text
    """
    punctuation_map = dict((ord(char), None) for char in string.punctuation)

    text = text.translate(punctuation_map)
    text = re.sub(r"\n+", '\n', text).strip()
    text = re.sub("\n", ' ', text).strip()
    text = re.sub(r"([0-9])([\u0400-\u04FF]|[A-z])", r"\1 \2", text)
    
    return tokenize(text, stop_words, lang)


# read ukrainian stop words
with open('./stop_words_ua.txt', encoding='utf-8') as file:
    uk_stop_words = set(file.read().splitlines())


normalize_partial = functools.partial(normalize, stop_words=uk_stop_words)
vectorizer = TfidfVectorizer(tokenizer=normalize_partial)

def cosine_sim(input_doc: str, corpus: List[str]) -> float:
    corpus.append(input_doc)

    tfidf = vectorizer.fit_transform(corpus)
    similarity_matrix = (tfidf * tfidf.T).A
    np.fill_diagonal(similarity_matrix, np.nan)

    return np.nanmax(similarity_matrix[-1])    


if __name__ == "__main__":
    folder = './test_files'
    input_path_1 = f'{folder}/MpiLab1.docx'
    input_path_2 = f'{folder}/MpiLab1_plag.docx'

    input_doc_1 = textract.process(input_path_1).decode('utf-8')
    input_doc_2 = textract.process(input_path_2).decode('utf-8')
    
    from hashes.simhash import simhash
    hash1 = simhash(normalize(input_doc_1, uk_stop_words))
    hash2 = simhash(normalize(input_doc_2, uk_stop_words))

    print([hash1.hex(), hash2.hex()])
    print(hash1.similarity(hash2))