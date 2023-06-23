# vim: set ts=2 sw=2 tw=99 noet:
import os
import pickle

class Cache:
	def __init__(self, path):
		self.vars = { }
		self.path = path

	def CacheVariable(self, name, value):
		self.vars[name] = value

	def WriteCache(self):
		f = open(self.path, 'wb')
		try:
			pickle.dump(self.vars, f)
		except Exception as e:
			raise e
		finally:
			f.close()

	def LoadCache(self):
		with open(self.path, 'rb') as f:
			try:
				self.vars = pickle.load(f)
			except Exception as e:
				f.close()
				raise e

	def HasVariable(self, key):
		return key in self.vars

	def __getitem__(self, key):
		return self.vars[key]

