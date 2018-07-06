from ..dataset.dataset import Dataset
from ..dataset import nexus
from ..helper import random_string
import os
from tqdm import tqdm
import numpy as np
import random
from pathos.multiprocessing import Pool
from ..network.network import SplitNetwork
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from .result import Result


def _as_nexus_file(data: Dataset, out_path, loci: list):

		temp = random_string(32)+'.nex'
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
			nexus.writeFooter(fp, ['chartransform=JukesCantor','SplitsPostProcess filter=weight value=1E-6'])

		return temp_file


def _partition(data: Dataset, out_path, num_partitions: int, num_loci: int, num_cores: int):

	if num_loci == 0:
		loci = range(data.num_loci)
	else:
		loci = random.sample(range(data.num_loci), num_loci)

	loci = list(loci)

	if data.diploid:
		loci + [x+data.num_loci for x in loci]

	parts = np.array_split(loci, num_partitions)

	part_files = [_as_nexus_file(data, out_path, x) for x in parts]

	sn = SplitNetwork()

	def func(file):
		return sn.execute_nexus_file(file)

	p = Pool(num_cores)

	return p.map(func, part_files)


def _r_forests(partitions: list, populations: list, num_splits: int, num_estimators: int, num_cores: int):
	kf = KFold(n_splits=num_splits, shuffle=True)

	populations = np.array(populations)

	predicted_origin_out = []
	mixture_estimate_out = []
	ordering_out = []

	for train, test in kf.split(partitions[0]):

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

	return np.array(predicted_origin_out)[indices], np.array(mixture_estimate_out)[indices], list(np.sort(np.unique(populations)))

class CrossValidate(Result):

	def __init__(self, dataset: Dataset, out_path: str):
		"""Runs Mycorrhiza with k-fold cross-validation.

		Args:
			dataset (Dataset): Dataset on which to run the analysis.
			out_path (str): Path to output folder.
		"""
		super().__init__(dataset, out_path)

	def run(self, n_partitions: int=1, n_loci: int=0, n_splits: int=5, n_estimators: int=60, n_cores: int=1) -> Result:
		"""Run the analysis with specified parameters.

		Args:
			n_partitions (int): Number of partitions in which to divide the loci sequentially.
			n_loci (int): Number of randomly selected loci to use (0 for all loci).
			n_splits (int): Number of cross-validation splits.
			n_estimators (int): Number of trees in the Random Forest classifier.
			n_cores (int): Number of cores.
		"""

		parts = _partition(self._dataset, self._out_path, n_partitions, n_loci, n_cores)
		pred_pops, q, q_pops = _r_forests(parts, self._dataset.populations, n_splits, n_estimators, n_cores)

		self.set_pred_pops(pred_pops)
		self.set_q(q, q_pops)

		self.output_q()

		return self


