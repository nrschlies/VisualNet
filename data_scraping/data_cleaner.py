"""
@package data_scraping.data_cleaner
@brief Provides data cleaning and preprocessing functionalities.

This module contains classes and functions for cleaning and preprocessing data,
including removing HTML tags, handling special characters, normalizing text,
and cleaning pandas DataFrames.

@class DataCleaner
@brief A class for cleaning and preprocessing data.
@date 2024-07-01
@license MIT
@dependencies
- re - Python Software Foundation License
- pandas - BSD 3-Clause License
- nltk - Apache License 2.0
"""

import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

class DataCleaner:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def remove_html_tags(self, text):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    def remove_special_characters(self, text, remove_digits=False):
        pattern = r'[^a-zA-Z\s]' if not remove_digits else r'[^a-zA-Z\s\d]'
        text = re.sub(pattern, '', text)
        return text

    def to_lowercase(self, text):
        return text.lower()

    def remove_stopwords(self, text):
        tokens = word_tokenize(text)
        filtered_tokens = [word for word in tokens if word.lower() not in self.stop_words]
        return ' '.join(filtered_tokens)

    def stem_text(self, text):
        tokens = word_tokenize(text)
        stemmed_tokens = [self.stemmer.stem(word) for word in tokens]
        return ' '.join(stemmed_tokens)

    def lemmatize_text(self, text):
        tokens = word_tokenize(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        return ' '.join(lemmatized_tokens)

    def normalize_text(self, text, remove_html=True, remove_special_chars=True, to_lower=True,
                       remove_stopwords=True, use_stemming=False, use_lemmatization=False):
        if remove_html:
            text = self.remove_html_tags(text)
        if remove_special_chars:
            text = self.remove_special_characters(text)
        if to_lower:
            text = self.to_lowercase(text)
        if remove_stopwords:
            text = self.remove_stopwords(text)
        if use_stemming:
            text = self.stem_text(text)
        if use_lemmatization:
            text = self.lemmatize_text(text)
        return text

    def clean_dataframe(self, df):
        return df.dropna().reset_index(drop=True)

    def clean_column(self, df, column_name, remove_html=True, remove_special_chars=True, to_lower=True,
                     remove_stopwords=True, use_stemming=False, use_lemmatization=False):
        df[column_name] = df[column_name].apply(lambda text: self.normalize_text(
            text,
            remove_html=remove_html,
            remove_special_chars=remove_special_chars,
            to_lower=to_lower,
            remove_stopwords=remove_stopwords,
            use_stemming=use_stemming,
            use_lemmatization=use_lemmatization
        ))
        return df

    def drop_duplicate_rows(self, df):
        return df.drop_duplicates().reset_index(drop=True)

    def drop_columns(self, df, columns):
        return df.drop(columns=columns)

    def fill_missing_values(self, df, strategy='mean'):
        if strategy == 'mean':
            return df.fillna(df.mean())
        elif strategy == 'median':
            return df.fillna(df.median())
        elif strategy == 'mode':
            return df.fillna(df.mode().iloc[0])
        else:
            raise ValueError(f"Unsupported fill strategy: {strategy}")

    def encode_categorical_columns(self, df):
        return pd.get_dummies(df)

    def normalize_dataframe(self, df):
        return (df - df.min()) / (df.max() - df.min())
