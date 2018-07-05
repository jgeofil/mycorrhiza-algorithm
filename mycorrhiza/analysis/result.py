import numpy as np
from typing import List
from ..dataset.dataset import Dataset
from os import path


class Result:

	def __init__(self, dataset: Dataset, out_path):

		self._out_path = out_path
		self._q_matrix = None
		self._q_pops = None
		self._dataset = dataset
		self._pred_populations = None

	@property
	def q_matrix(self):
		return self._q_matrix

	@property
	def q_populations(self):
		return self._q_pops

	@property
	def pred_populations(self):
		return self._pred_populations

	@property
	def real_populations(self):
		return self._dataset.populations

	@property
	def identifiers(self):
		return self._dataset.identifiers

	def set_pred_pops(self, pops: List):
		self._pred_populations = pops

	def set_q(self, q: List[List], col_pops: List):

		q = np.array(q)

		if q.shape[1] > q.shape[0]:
			raise ValueError('Q matrix cannot have more populations (cols) than samples (rows).')

		if q.shape[1] != len(col_pops):
			raise ValueError('Population column identifiers length mismatch.')

		if q.shape[0] != len(self.identifiers):
			raise ValueError('Mismatch in the number of samples.')

		self._q_matrix = q
		self._q_pops = col_pops

	def output_q(self, file_name: str='Q'):
		out_file = path.join(self._out_path, '{0}.tsv'.format(file_name))

		with open(out_file, 'w+') as fout:
			fout.write('samples\t{0}\n'.format('\t'.join(self._q_pops)))
			for iden, line in zip(self._dataset.identifiers, self.q_matrix):
				fout.write('{0}\t{1}\n'.format(iden, '\t'.join(line.astype(str))))


