#!/usr/bin/python3.7
# coding: utf-8

import importlib
import site
import os

datapath = os.path.dirname(os.path.abspath(__file__))

site.addsitedir(datapath)
site.addsitedir(datapath + "/data")

from forestbot import ForestBot
from tfidfbot import TfidfBot

class MasterBot:
    def __init__(self):
        self.forestbot = ForestBot()
        self.tfidfbot = TfidfBot()

    def answer(self, question):    
        score, ans, cat = self.forestbot.answer(question)
        score_tf, ans_tf = self.tfidfbot.answer(question)
        
        print("[masterbot] forest:", cat, score, ans, "tfidf:", score_tf, ans_tf)
        if score > score_tf:
            return cat, ans
        return "tfidf", ans_tf

    def reload(self):
        #importlib.reload(ForestBot)
        #importlib.reload(TfidfBot)
        self.forestbot.reload()
        self.tfidfbot.reload()


if __name__ == "__main__":
    mb = MasterBot()
    print("Chatbot Hilde v0.2a\nWrite 'exit' to leave")
    while True:
    	question = input("\n>>> ")
    	if question == "exit": break
    	antwoord = mb.answer(question)
    	print("Hilde:", antwoord)