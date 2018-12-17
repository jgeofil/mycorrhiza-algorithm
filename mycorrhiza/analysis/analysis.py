import numpy as np
from typing import List
from ..dataset.dataset import Dataset
from os import path
from ..dataset import nexus
from ..helper import random_string
import os
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

		if os.path.isfile(out_file):
			os.remove(out_file)

		with open(out_file, 'w+') as fout:
			fout.write('samples\t{0}\n'.format('\t'.join(self._q_pops)))
			for iden, line in zip(self._dataset.identifiers, self.q_matrix):
				fout.write('{0}\t{1}\n'.format(iden, '\t'.join(line.astype(str))))

	def output_accuracy(self, file_name: str='acc'):
		out_file = path.join(self._out_path, '{0}.tsv'.format(file_name))

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


def _as_nexus_file(data: Dataset, out_path, loci: list):

	temp = random_string(32) + '.nex'
	temp_file = os.path.join(out_path, temp)

	with open(temp_file, 'w+') as fp:
		nexus.writeHeader(fp, 'SEQUENCES', data.num_samples)
		nexus.start_characters_block(fp, len(loci))

		count = 0
		with tqdm(total=data.num_samples, desc='Outputting data in Nexus format.') as progress:
			for sample, genotype in data.iterator():
				progress.update(1)

				nexus.write_characters_line(fp, count, sample.identifier, np.array(genotype)[loci])
				count += 1
		nexus.end_block(fp)
		nexus.writeFooter(fp, ['chartransform=JukesCantor', 'SplitsPostProcess filter=weight value=1E-6'])

	return temp_file


def _partition(data: Dataset, out_path, num_partitions: int, num_loci: int, num_cores: int):
	if num_loci == 0:
		loci = range(data.num_loci)
	else:
		loci = random.sample(range(data.num_loci), num_loci)

	loci = list(loci)

	if data.diploid:
		loci + [x + data.num_loci for x in loci]

	parts = np.array_split(loci, num_partitions)

	part_files = [_as_nexus_file(data, out_path, x) for x in parts]

	sn = SplitNetwork()

	def func(file):
		return sn.execute_nexus_file(file)

	p = Pool(num_cores)

	return p.map(func, part_files)


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