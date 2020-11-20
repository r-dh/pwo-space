import json
import re
import unicodedata
import hashlib

class TextToHash:
    def __init__(self):
        self.cache = {}

    def _unicode_to_ascii(self, s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn')

    def _clean_data(self, w):
        w = self._unicode_to_ascii(w.lower().strip())
        w = re.sub(r"([?.!,¿])", r" ", w)
        w = re.sub(r"[^a-zA-Z?.!,¿]+", " ", w)
        w = re.sub(r'[" "]+', " ", w)
        w = w.rstrip().strip()
        return w
    
    def hash(self, s):
        if not s in self.cache:
            self.cache[s] = str(int(hashlib.sha1(self._clean_data(s).encode('utf-8')).hexdigest(), 16))
        return self.cache[s]