#!/usr/bin/python3.7
# coding: utf-8
import numpy as np
import random

import os
import sys
import re
import unicodedata
import glob
import time

from joblib import load

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

#from data import run_update_scripts
from data import data_to_classifier
from data.database import Database, singleton
# class Chatbot:
#     def __init__():  

@singleton
class ForestBot:
    def __init__(self):
        self.db = Database()
        self.loadData();

    def loadData(self):
        datapath = os.path.dirname(os.path.abspath(__file__)) + "/data/"
        classifier_path = str(datapath + "/bart_randforest_cls.pkl")
        tfidf_path = str(datapath + "/bart_randforest_tfidf.pkl")

        if not glob.glob(datapath + "*.pkl"):  
            print("[SPACEAPP] ForestBot: Initialising a fresh install...")
            data_to_classifier.execute(self.db, datapath)

            timeout = 5
            sec = 0
            while not os.path.isfile(classifier_path) or not os.path.isfile(tfidf_path):
                time.sleep(1)
                sec += 1
                if sec > timeout:
                    print(f"[SPACEAPP] ForestBot: File generation timed out after {timeout} seconds")
                    break

        if not os.path.isfile(classifier_path) or not os.path.isfile(tfidf_path):
            print("[SPACEAPP] ForestBot: No classifiers present")
            return None

        self.text_classifier = load(classifier_path)
        self.tfidfconverter = load(tfidf_path)
        print("[SPACEAPP] ForestBot: Loaded data")


    def _predict(self, question):
        return self.text_classifier.predict(self.tfidfconverter.transform([question]))

    def answer(self, question):
        category = self._predict(self.__clean_data(question))[0]
        mylist = self.text_classifier.predict_proba(self.tfidfconverter.transform([question]))
        return (mylist.max(), random.choice(self.db.get_category_answers(category)), category)
        #return mylist.max(), random.choice([y for (x,y) in answers if x == category]), category[0]

    def reload(self):
        self.loadData();
        self.db.reload();

    def __unicode_to_ascii(self, s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn')

    def __clean_data(self, w):
        w = self.__unicode_to_ascii(w.lower().strip())
        w = re.sub(r"([?.!,¿])", r" \1 ", w)
        w = re.sub(r'[" "]+', " ", w)
        w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)
        w = w.rstrip().strip()
        return w



if __name__ == "__main__":
    fb = ForestBot()
    print("Chatbot Bart v0.2a\nWrite 'exit' to leave")
    while True:
        question = input("\n>>> ")
        if question == "exit": break
        antwoord = fb.answer(question)
        print("Bart:", antwoord)