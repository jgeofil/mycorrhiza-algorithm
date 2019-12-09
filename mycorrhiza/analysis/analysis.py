import numpy as np
from typing import List
from ..dataset.dataset import Dataset
from ..dataset import nexus
from ..helper import random_string
from tqdm import tqdm
import random
from pathos.multiprocessing import Pool
from ..network.network import SplitNetwork
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import os
from collections import Counter

class Result:

	def __init__(self, dataset: Dataset, out_path):

		if not os.path.exists(out_path):
			os.makedirs(out_path)

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

	def set_q_pred_pops_params(self, predicted_origin, probabilities, classes, test_indices=[], train_indices=[]):
		'''
		@TBD
		'''
		if not test_indices and not train_indices:
			raise ValueError("Either test or train indices must be provided.")
		elif not test_indices:
			test_indices = [ind for ind in range(len(self.real_populations)) if ind not in train_indices]
		elif not train_indices:
			train_indices = [ind for ind in range(len(self.real_populations)) if ind not in test_indices]
		
		out_q = []
		out_origin = []
		for i in np.sort(test_indices + train_indices):
			if i in test:
				out_q.append(probabilities[test.index(i)])
				out_origin.append(predicted_origin[test.index(i)])
			else:
				out_q.append([1 if x == list(classes).index(self.real_populations[i]) else 0 for x in range(len(classes))])
				out_origin.append(self.real_populations[i])

		out_origin, out_q = np.array(out_origin), np.array(out_q)

		self.set_pred_pops(pred_pops)
		self.set_q(out_q, classes)

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
		out_file = os.path.join(self._out_path, '{0}.tsv'.format(file_name))

		if os.path.isfile(out_file):
			os.remove(out_file)

		with open(out_file, 'w+') as fout:
			fout.write('samples\t{0}\n'.format('\t'.join(self._q_pops)))
			for iden, line in zip(self._dataset.identifiers, self.q_matrix):
				fout.write('{0}\t{1}\n'.format(iden, '\t'.join(line.astype(str))))

	def output_accuracy(self, file_name: str='acc'):
		out_file = os.path.join(self._out_path, '{0}.tsv'.format(file_name))

		if os.path.isfile(out_file):
			os.remove(out_file)
		
		acc = accuracy_score(self.real_populations, self._pred_populations)
		print('Accuracy: {0}\n'.format(acc))

		with open(out_file, 'w+') as fout:
			fout.write('Accuracy: {0}\n'.format(acc))
			fout.write('####')
			fout.write('samples\ttrue\tpred\n')
			for iden, re, pr in zip(self._dataset.identifiers, self.real_populations, self._pred_populations):
				fout.write('{0}\t{1}\t{2}\n'.format(iden, re, pr))


def _r_forests(partitions: list, populations: list, num_splits: int, num_estimators: int, num_cores: int):
	kf = StratifiedKFold(n_splits=num_splits, shuffle=True)

	counts = Counter(populations)
	for key in counts:
		if counts[key] < num_splits:
			raise ValueError("Population {0} has less samples ({1}) than the number of splits ({2}).".format(key, counts[key], num_splits))

	populations = np.array(populations)

	predicted_origin_out = []
	mixture_estimate_out = []
	ordering_out = []

	for train, test in kf.split(partitions[0], y=populations):

		mixture_estimates_per_partition = []
		clf = RandomForestClassifier(n_estimators=num_estimators, verbose=True, n_jobs=num_cores)
		for part in partitions:
			clf.fit(part[train], populations[train])
			mixture = clf.predict_proba(part[test])
			mixture_estimates_per_partition.append(mixture)

		mixture_estimate = np.mean(mixture_estimates_per_partition, axis=0)
		predicted_origin = [clf.classes_[np.argmax(x)] for x in mixture_estimate]

		predicted_origin_out += predicted_origin
		mixture_estimate_out += list(mixture_estimate)
		ordering_out += list(test)

	indices = np.argsort(ordering_out)

	return np.array(predicted_origin_out)[indices], np.array(mixture_estimate_out)[indices], list(
		np.sort(np.unique(populations)))


def _sup_r_forests(train: List[int], test: List[int], partitions: list, populations: list, num_estimators: int, num_cores: int):

	populations = np.array(populations)

	mixture_estimates_per_partition = []
	clf = RandomForestClassifier(n_estimators=num_estimators, verbose=True, n_jobs=num_cores)
	for part in partitions:
		clf.fit(part[train], populations[train])
		mixture = clf.predict_proba(part[test])
		mixture_estimates_per_partition.append(mixture)

	mixture_estimate = np.mean(mixture_estimates_per_partition, axis=0)
	predicted_origin = [clf.classes_[np.argmax(x)] for x in mixture_estimate]

	out_q = []
	out_origin = []
	for i in np.sort(train+test):
		if i in test:
			out_q.append(mixture_estimate[test.index(i)])
			out_origin.append(predicted_origin[test.index(i)])
		else:
			out_q.append([1 if x == list(clf.classes_).index(populations[i]) else 0 for x in range(len(clf.classes_))])
			out_origin.append(populations[i])

	return np.array(out_origin), np.array(out_q), clf.classes_