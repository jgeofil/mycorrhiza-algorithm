import numpy as np
from .. import nexus
import random
import os

from tqdm import tqdm
from pathos.multiprocessing import Pool

from ..dataset import Dataset
from ...helper import random_string
from ...network.network import SplitNetwork

def _as_nexus_file(data: Dataset, out_path, loci: list):

	temp = random_string(32) + '.nex'
	temp_file = os.path.join(out_path, temp)

	with open(temp_file, 'w+') as fp:
		nexus.writeHeader(fp, 'MYCORRHIZA', data.num_samples)
		if data.is_str:
			nexus.writeDistancesBlock(fp, data._microsatellite_distances(), data.identifiers)
			nexus.writeFooter(fp, ['SplitsPostProcess filter=weight value=1E-6'])
		else:
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