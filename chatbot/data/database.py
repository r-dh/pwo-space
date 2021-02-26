

import os
import json
import functools

def singleton(cls):
    """Make a class a Singleton class (only one instance)"""
    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance
    wrapper_singleton.instance = None
    return wrapper_singleton

def validate_category(*expected_args):
	def decorator_validate_category(func):
		@functools.wraps(func)
		def wrapper_validate_category(self, *args, **kwargs):
			for arg in args:
				if arg not in self._db:
					print(f"WARNING: {arg} not found in db, returning None")
					return None

				for expected_arg in expected_args:
					if expected_arg not in self._db[arg]:
						print(f"WARNING: {expected_arg} not found in db[{arg}], returning None")
						return None
			return func(self, *args, **kwargs)
		return wrapper_validate_category
	return decorator_validate_category

@singleton
class Database:
	_db = {}

	def _open(self):
		filepath = os.path.dirname(__file__) + "/bart_data.json"
		assert(os.path.isfile(filepath))
		with open(filepath, 'r') as file:
			self._db = json.load(file)
	
	def reload(self):
		self._open()

	def __init__(self):
		self._db = {}
		self._open()
		#print("Loaded database: " + str(len(self._db.keys())) + " categories")
	
	## returns list of categories
	def get_categories(self):
		return list(self._db.keys())
	
	## questions and answers lists in category
	@validate_category()
	def get_category(self, category):
			return self._db[category]
	
	## returns list of answers in category
	@validate_category("answers", "questions")
	def get_category_answers(self, category):
		return self._db[category]["answers"]
	
	## returns list of questions in category
	@validate_category("answers", "questions")
	def get_category_questions(self, category):
		return self._db[category]["questions"]



