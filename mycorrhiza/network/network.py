from ..dataset import nexus
from ..settings import const
import subprocess
import os
import numpy as np

class SplitNetwork:

	def __init__(self):
		self._weights = None
		self._splits = None
		self._ordering = None

	def _set_splits(self, splits, weights, ordering):

		self._ordering = np.array(ordering)
		self._weights = np.array(weights)
		self._splits = np.array(splits)

	def getSplitsMatrix(self):
		return np.array(self._splits).T

	def execute_nexus_file(self, filename, delete_file=False):
		print('Building network from file {0}'.format(filename))
		bash_nexus_file(filename)

		self._set_splits(*nexus.readSplitsBlock(filename))

		if delete_file:
			os.unlink(filename)

		return self.getSplitsMatrix()


def bash_nexus_file(filename):

	bash_command = '{0} -g -v -i {1}'.format(const['__SPLITSTREE_PATH__'], os.path.abspath(filename))

	print(bash_command)

	process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()

	if error:
		raise RuntimeError(error)
	else:
		return True

