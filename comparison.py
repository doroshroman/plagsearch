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


class TextProcessor:
    def __init__(self, document_path, stop_words_path='./stop_words_ua.txt', lang='uk'):
        self.lang = lang
        self.morph = pymorphy2.MorphAnalyzer(lang=self.lang)
        self.text = textract.process(document_path).decode('utf-8')
        self.stop_words = self._read_stop_words(stop_words_path)

    def _read_stop_words(self, words_path):
        with open(words_path, encoding='utf-8') as file:
            return set(file.read().splitlines())

    def tokenize(self, text) -> List[str]:
        tokenized_list = []
        sentences = nltk.sent_tokenize(self.text)

        for sentence in sentences:
            words = nltk.word_tokenize(sentence)
            digits_to_words = [
                num2words(
                    word,
                    lang=self.lang) if word.isdigit() else word for word in words]
            words_lower = [word.lower() for word in digits_to_words]
            words_without_stop = [word for word in words_lower if word not in self.stop_words]
            for token in words_without_stop:
                parsed = self.morph.parse(token)[0]
                tokenized_list.append(parsed.normal_form)

        return tokenized_list
    
    def normalize(self) -> List[str]:
        """Remove  punctuation, multiple new line, 
        Return tokenized text
        """
        punctuation_map = dict((ord(char), None) for char in string.punctuation)

        self.text = self.text.translate(punctuation_map)
        self.text = re.sub(r"\n+", '\n', self.text).strip()
        self.text = re.sub("\n", ' ', self.text).strip()
        self.text = re.sub(r"([0-9])([\u0400-\u04FF]|[A-z])", r"\1 \2", self.text)
        
        return self.tokenize(self.text)


# normalize_partial = functools.partial(normalize, stop_words=uk_stop_words)
# vectorizer = TfidfVectorizer(tokenizer=normalize_partial)

# def cosine_sim(input_doc: str, corpus: List[str]) -> float:
#     corpus.append(input_doc)

#     tfidf = vectorizer.fit_transform(corpus)
#     similarity_matrix = (tfidf * tfidf.T).A
#     np.fill_diagonal(similarity_matrix, np.nan)

#     return np.nanmax(similarity_matrix[-1])    


if __name__ == "__main__":
    # folder = './test_files'
    # input_path_1 = f'{folder}/MpiLab1.docx'
    # input_path_2 = f'{folder}/MpiLab1_plag.docx'

    # processor = TextProcessor(input_path_1, './stop_words_ua.txt') 
    # from web.utils import Hash
    # hash = Hash(processor.normalize())
    # print(hash.sha256())
    # from hashes.simhash import simhash
    # hash1 = simhash(normalize(input_doc_1, uk_stop_words))
    # hash2 = simhash(normalize(input_doc_2, uk_stop_words))

    # print([hash1.hex(), hash2.hex()])
    # print(hash1.similarity(hash2))