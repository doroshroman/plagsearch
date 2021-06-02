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
from config import basedir
import os
from .utils import Hash
import hashes.hashtype as ht
from hashes.hashtype import hashtype
from itertools import islice


try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt')


class TextProcessor:
    def __init__(self, document_path, stop_words_path=None, lang='uk'):
        self.lang = lang
        self.morph = pymorphy2.MorphAnalyzer(lang=self.lang)
        self.text = textract.process(document_path).decode('utf-8')
        if not stop_words_path:
            stop_words_path = os.path.join(basedir, 'stop_words_ua.txt')
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


def compare(doc_simhash, doc_sha256, simhashes, sha256hashes, limit=10):
    doc_hs = hashtype(hash=int(doc_simhash))
    
    # remove the same item
    ind = sha256hashes.index(doc_sha256) if doc_sha256 in sha256hashes else -1
    if ind != -1:
        del simhashes[ind]

    report = {h: hash_similarity(doc_hs, hashtype(hash=int(h))) for h in simhashes}
    sorted_report = list(sorted(islice(report.items(), limit), key=lambda item: item[1], reverse=True))
    
    return sorted_report


def hash_similarity(hash, other_hash, hashbits=None):
    if not hashbits:
        hashbits = ht.default_hashbits
    
    return float(hashbits - hash.hamming_distance(other_hash)) / hashbits

