# vim: set ts=2 sw=2 tw=99 noet: 
import os
import traceback
import ambuild.worker as worker
from ambuild.cache import Cache
from ambuild.command import Command

class TaskGroup:
	def __init__(self, cmds, mustBeSerial = True):
		self.cmds = cmds
		self.mustBeSerial = mustBeSerial

class AsyncRun:
	def __init__(self, master, job, task):
		self.master = master
		self.task = task
		self.job = job
	def run(self):
		spewed = False
		try:
			self.task.run(self.master, self.job)
			spewed = True
			self.task.spew(self.master)
		except Exception as e:
			try:
				if not spewed:
					self.task.spew(self.master)
			except:
				pass
			raise Exception(str(e) + '\n' + traceback.format_exc())

class Job:
	def __init__(self, runner, name, workFolder = None):
		self.tasks = []
		self.name = name
		self.runner = runner
		self.workFolder = name if workFolder is None else workFolder
		self.cache = Cache(
			os.path.join(runner.outputFolder, '.ambuild', f'{name}.cache')
		)
		#ignore if cache file doesnt exist yet
		try:
			self.cache.LoadCache()
		except:
			pass

	def CacheVariable(self, key, value):
		self.cache.CacheVariable(key, value)

	def HasVariable(self, key):
		return self.cache.HasVariable(key)

	def GetVariable(self, key):
		return self.cache[key]
	
	def AddCommand(self, cmd):
		if not isinstance(cmd, Command):
			raise Exception('task is not a Command')
		self.tasks.append(TaskGroup([cmd]))

	def AddCommandGroup(self, cmds, mustBeSerial = True):
		if not isinstance(cmds, list):
			raise Exception('tasks are not in a list')
		self.tasks.append(TaskGroup(cmds, mustBeSerial))

	def run(self, master):
		for group in self.tasks:
			for task in group.cmds:
				r = AsyncRun(master, self, task)
				try:
					r.run()
				except Exception as e:
					self.cache.WriteCache()
					raise e
				self.cache.WriteCache()

