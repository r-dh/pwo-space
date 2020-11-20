#!/usr/bin/env python
# coding: utf-8

# In[729]:


import numpy as np
import pickle

import nltk
nltk.download('stopwords', quiet = True)
nltk.download('punkt') 
from nltk.corpus import stopwords

import os
import re
import unicodedata
import math

import json
from data.database import Database, singleton

@singleton
class TfidfBot:

    def __init__(self):
        # datapath = str(os.path.dirname(__file__))
        # path = datapath + "/data/hilde_data.json"
        # if not os.path.isfile(path):
        #     path = str(os.getcwd() + "/data/hilde_data.json")
        
        # with open(path, 'r') as file:
        #     self.data = json.load(file)
        
        # if "tfidf" not in data:
        #     print("[tfidfbot] tfidf not found in data...")
        #     self.corrected = { "test test": "Test?" }
        # else:
        #     self.corrected = self.data["tfidf"]
        
        self.db = Database()
        self.tokenize_cache = {}
        
        
        
    # def clean(corrected):    
    #     ## Create list of documents to match
    #     train_data = []
    #     train_data = list(corrected.keys())
    #     #train_data
        
        
    #     # ## Clean up data
        
    #     # In[732]:
        
        
    #     ## Optionally remove stopwords 
    #     cleaned_data = []
    #     for s in train_data:
    #         #print(s, " --> ", clean_data(s), " --> ", remove_stopwords(clean_data(s)))
    #         #cleaned_data.append(remove_stopwords(clean_data(s)))
    #         cleaned_data.append(clean_data(s))
        
    #     train_data = cleaned_data
    #     return train_data


    # In[704]:


    ## Create a stopword list from the standard list of stopwords available in nltk
    #stop_words = set(stopwords.words('dutch'))
    #print(len(stop_words))


    # In[705]:


    ## Create helper functions
    def _unicode_to_ascii(self, s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn')

    def clean_data(self, w):
        w = self._unicode_to_ascii(w.lower().strip())

        # creating a space between a word and the punctuation following it
        # eg: "he is a boy." => "he is a boy ."
        # Reference:- https://stackoverflow.com/questions/3645931/python-padding-punctuation-with-white-spaces-keeping-punctuation
        w = re.sub(r"([?.!,¿]+)", r" \1 ", w)
        w = re.sub(r'[" "]+', " ", w)

        # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
        w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)

        w = w.rstrip().strip()

        # adding a start and an end token to the sentence
        # so that the model know when to start and stop predicting.
        ### w = '<start> ' + w + ' <end>'
        return w

    def tokenize(self, document):
        if document not in self.tokenize_cache:
            self.tokenize_cache[document] = nltk.word_tokenize(document)
        return self.tokenize_cache[document]

    def remove_stopwords(self, document):
        return ' '.join([word for word in self.tokenize(document) if word not in stop_words])





    # ## Different ways of determining Term Freqency

    # Binary:
    # $$0,1$$

    # In[707]:


    def term_binary_frequency(self, term, document):
        return 1 if self.tokenize(document).count(term) else 0


    # Raw frequency:
    #     $$f_{t, d}$$

    # In[708]:


    def term_raw_frequency(self, term, document):
        return self.tokenize(document).count(term)


    # Term frequency:
    # $$\frac{f_{t, d}}{\sum\limits_{t' \in d}{f_{t', d}}}$$
    # 
    # 

    # In[709]:


    def term_frequency(self, term, document):
        return self.tokenize(document).count(term)/len(self.tokenize(document))


    # Augmented frequency:
    # $$\mbox{tf}_{t,d} = 0.5+0.5\cdot\frac{f_{t, d}}{max\{f_{t', d}:t'\in d \}}$$

    # In[710]:


    ## Use to prevent a bias towards longer documents
    def term_augmented_frequency(self, term, document):
        max_term_freq = max([self.term_raw_frequency(token, document) for token in self.tokenize(document)])
        #print(self.term_raw_frequency(term, document), max_term_freq)
        return 0.5 + 0.5 * (self.term_raw_frequency(term, document)/max_term_freq)


    # Log frequency:
    # $$\mbox{tf}_{t, d} =  \begin{cases} \log(1 + \mbox{f}_{t,d}), &\mbox{if f}_{t,d}>0  \\ 0, & \mbox{otherwise} \end{cases}$$

    # In[711]:


    def term_log_frequency(self, term, document):
        #print(term_frequency(term, document))
        freq = self.term_frequency(term, document)
        return 0 if freq is 0 else math.log(1 + freq)


    # ## Inverse Document Frequency

    # idf weight $n_t = |\{d \in D: t \in d\}|$
    # 
    # inverse document frequency smooth:
    # $$\log \left( \frac {N} {1 + n_t}\right)+ 1$$
    # 
    # $$ \mathrm{idf}(t, D) =  \log \frac{N}{|\{d \in D: t \in d\}|}$$
    # 
    # with
    # * $N$: total number of documents in the corpus $N = {|D|}$
    # * $ |\{d \in D: t \in d\}| $ : number of documents where the term $ t $ appears (i.e., $ \mathrm{tf}(t,d) \neq 0$). If the term is not in the corpus, this will lead to a division-by-zero. It is therefore common to adjust the denominator to $1 + |\{d \in D: t \in d\}|$.

    # In[712]:


    ## make sure that "documents" is a list
    # TODO: IDF generates strongly positive numbers when there are lots of documents
    #       and just a few documents containing the term
    def inverse_document_frequency(self, term, documents):
        contains_token = map(lambda document : term in self.tokenize(document), documents)
        #print(term, list(map(lambda sentence : term in tokenize(sentence), documents)))
        return math.log(len(documents)/(1 + sum(contains_token)))+1     


    # Calculate the idf for all tokens

    # In[713]:

    # ## Term frequency–Inverse document frequency
    # $$\mathrm{tfidf}(t,d,D) = \mathrm{tf}(t,d) \cdot \mathrm{idf}(t, D)$$

    # In[714]:


    def tfidf(self, term, document, documents):
        idf = round(self.inverse_document_frequency(term, documents),2)
        # print(term, "in", document, "IDF:", idf)
        # print("TB:", self.term_binary_frequency(term, document))
        # print("TF:", self.term_frequency(term, document))
        # print("TR:", self.term_raw_frequency(term, document))
        # print("TA:", self.term_augmented_frequency(term, document))    
        # print("TL:", self.term_log_frequency(term, document))
        return self.term_frequency(term, document) * self.inverse_document_frequency(term, documents)


    def cosine_similarity(self, vec1, vec2):
        dot_product = sum(a*b for a,b in zip(vec1, vec2))
        magnitude = math.sqrt(sum([a**2 for a in vec1])) * math.sqrt(sum([b**2 for b in vec2]))
        if magnitude == 0:
            return 0
        return dot_product/magnitude


    # In[718]:


    def lookup(self, query, documents):
        query = self.clean_data(query)

        if not query or not documents:
            print(f"ERROR: no query or replies given\nquery: {query}")
        
        # vectorize query
        idf_query = []
        for term in [t.strip() for t in self.tokenize(query) if t.strip()]:
            idf_query.append(self.tfidf(term, query, documents))
        
        #vectorize query in function of each document 
        similarity = []
        for doc in [d.strip() for d in documents if d.strip()]:
            idf_query_doc = []
            for term in [t.strip() for t in self.tokenize(query) if t.strip()]:
                idf_query_doc.append(self.tfidf(term, doc, documents))
            similarity.append((doc, self.cosine_similarity(idf_query, idf_query_doc)))
            #print(idf_query,":", idf_query_doc)
            similarity.sort(key=lambda x : x[1], reverse=True)
        return similarity


    # In[719]:

    def replies(self, query, dictReplies):
        # prepare data
        query = self.clean_data(query)
        dictReplies = { self.clean_data(k): dictReplies[k] for k in dictReplies.keys() }

        top_matches = self.lookup(query, list(dictReplies.keys()))
        result = []
        for document, rating in top_matches:
            if document == query:
                rating *= 10
            result.append((dictReplies[document], rating))
        return result


    # In[720]:


    def _answer(self, query, dictReplies):
        if not query or not dictReplies:
            print(f"ERROR: no query or replies given\nquery: {query}\nreplies: {dictReplies}")
        answers = self.replies(query, dictReplies)
        answers.sort(key=lambda x : x[1], reverse=True)
        a, b = answers[0]
        return (b, a) if b != 0 else (0, "Invalid question")

    def answer(self, query):
        return self._answer(query, self.db.get_category("tfidf"))

    def reload(self):
        self.db.reload();

if __name__ == "__main__":
    tf = TfidfBot()
    print("Chatbot Hilde v0.2a\nWrite 'exit' to leave")
    while True:
        question = input("\n>>> ")
        if question == "exit": break
        antwoord = tf.answer(question)
        print("Hilde:", antwoord)