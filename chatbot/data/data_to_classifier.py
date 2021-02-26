
import os
import random
import pathlib

import pandas as pd
import numpy as np
import nltk
nltk.download('stopwords', quiet = True)  
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

from database import Database



def load_data(path, explicit = True):
	dataset = np.load(path)
	
	labels, data = zip(*dataset)
	
	if explicit:
		print("Categories:", len(set(labels)))
		print("Data:", len(data))
		print("Entries per class:", len(data)/len(set(labels)))

	return labels, data

def filter_data(dataset, n = 4):	
	df = pd.DataFrame(dataset)
	df_labels = df.groupby(0).size().reset_index(name='counts')
	df_labels = df_labels[df_labels["counts"] >= n]
	df = df.loc[df[0].isin(df_labels[0])]
	
	print("Applying filter, removing categories under", n, "data entries...")
	
	dataset = df.to_numpy()
	labels, data = zip(*dataset)
	
	print("Categories:", len(set(labels)))
	print("Data:", len(data))
	print("Entries per class:", len(data)/len(set(labels)))
	return labels, data

def converter(labels, data):
	tfidfconverter = TfidfVectorizer(max_features=1000, min_df=0.0020, max_df=0.1, stop_words=stopwords.words('dutch'))  #todo test without stopwords
	
	data = tfidfconverter.fit_transform(data).toarray()
	
	X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.01, random_state=0) # overfitting ftw, we don't need test results for production model, we need actual results (so we use all available data)
	
	text_classifier = RandomForestClassifier(n_estimators=250, random_state=0)  
	text_classifier.fit(X_train, y_train)	
	
	predictions = text_classifier.predict(X_test)
	
	report = classification_report(y_test,predictions)
	print(report)
	score = accuracy_score(y_test, predictions)
	print("Final accuracy:", score)
	return text_classifier, tfidfconverter, score, report


def save(text_classifier, tfidfconverter, path): #todo pimp path
	if len(path) == 0:
		path = str(os.path.dirname(__file__))
	result = joblib.dump(text_classifier, str(path + '/bart_randforest_cls.pkl')) 
	joblib.dump(tfidfconverter, str(path + '/bart_randforest_tfidf.pkl'))
	print("Pickled randforest classifiers at " + str(result[0]))


def execute(db, path):
	# path = ""
	# try:
	# 	labels, data = load_data("data.npy")
	# except FileNotFoundError:
	# 	try:
	# 	#if os.name == "nt":
	# 		path = str(os.getcwd())
	# 		labels, data = load_data(str(os.getcwd() + "/data.npy"))
	# 	except:
	# 	#else:
	# 		path = str(os.path.dirname(__file__))
	# 		labels, data = load_data(str(os.path.dirname(__file__) + "/data.npy")) #toch windows? todo: check
	# # filter_data((labels, data), 4)
	labels = []
	data = []

	all_categories = db.get_categories()
	for cat in all_categories:
		answers = db.get_category_questions(cat)
		if answers is not None:
			print(cat + ": " + str(len(answers)))
			for answer in answers:
				labels.append(cat)
				data.append(answer)

	print(len(data))
	print(len(labels))
	text_classifier, tfidfconverter, score, report = converter(labels, data)
	save(text_classifier, tfidfconverter, path)#, path) # path
	return score, report

if __name__ == "__main__":
	db = Database()
	path = str(pathlib.Path(__file__).parent.absolute())
	#print(path)
	execute(db, path)
