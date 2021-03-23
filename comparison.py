#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import textract
import nltk
import re
import pymorphy2
from num2words import num2words


nltk.download('punkt')

morph = pymorphy2.MorphAnalyzer(lang='uk')

path = './test_files/MpiLab1.docx'

# extract text from document
text = textract.process(path).decode('utf-8')

def tokenize(text, stop_words, lang='uk'):
    tokenized_list = []

    text = re.sub(r"\n+", '\n', text).strip()
    text = re.sub("\n", ' ', text).strip()
    text = re.sub(r"[\\\.\,\:\+\-\*/_№;\(\)–]", ' ', text).strip()
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


# read ukrainian stop words
with open('./stop_words_ua.txt', encoding='utf-8') as file:
    uk_stop_words = set(file.read().splitlines())


print(tokenize(text, uk_stop_words))
