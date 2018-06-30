from ..load.load import Loader
from ..load import nexus
from ..helper import random_string
import os
from tqdm import tqdm
import numpy as np
import random
from pathos.multiprocessing import Pool
from ..splits.splits import SplitNetwork
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier


def _as_nexus_file(data: Loader, out_path, loci: list):

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


def _partition(data: Loader, out_path, num_partitions: int, num_loci: int, num_cores: int):

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


def _averaged_random_forests(partitions: list, populations: list, num_splits: int, num_estimators: int, num_cores: int):
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

	return np.array(predicted_origin_out)[indices], np.array(mixture_estimate_out)[indices]


def cross_validate(data: Loader,
					out_path,
					n_partitions: int=1,
					n_loci: int=0,
					n_splits: int=5,
					n_estimators: int=60,
					n_cores: int=1):

	parts = _partition(data, out_path, n_partitions, n_loci, n_cores)
	return _averaged_random_forests(parts, data.populations, n_splits, n_estimators, n_cores)