import os
from ..helper import random_string
from ..exceptions import LoadingError
import numpy as np
from tqdm import tqdm

_LINE_LEN = 80
_BUFFER_LEN = _LINE_LEN * 100

_GENOTYPE_START_COL = 9

_MISSING_CHAR = '.'


def _count_loci(path_in):
	start = False
	total = 0
	with open(path_in) as fin:
		for line in fin:
			if '#CHROM' in line:
				start = True
			if start:
				total += 1
	return total


def _get_identifiers(path_in):
	with open(path_in) as fin:
		line = ''
		while '#CHROM' not in line:
			line = fin.readline()
		return line.split()[_GENOTYPE_START_COL:]


def _empty_str(L):
	return ['' for _ in range(L)]


def _flush(fr, fl, gr, gf):
	for genoR, genoL, fileR, fileL in zip(gr, gf, fr, fl):
		fp = open(fileR, 'a')
		fp.write(genoR)
		fp.close()
		fp = open(fileL, 'a')
		fp.write(genoL)
		fp.close()

	return _empty_str(len(fr)), _empty_str(len(fr))


def _rep(c):
	return '-9' if c == _MISSING_CHAR else c


def _write_line(source_file, out_pointer, identifier, population):
	with open(source_file) as fin:
		out_pointer.write('{0} {1} 0 '.format(identifier, population))
		for line in fin:
			line = [_rep(x) for x in line.strip()]
			out_pointer.write(' '.join(line)+' ')
		out_pointer.write('\n')


def vcf_to_structure(path_in: str, path_out: str, populations: list, diploid: bool=True):
	"""Converts a VCF file into the STRUCTURE format.

	Args:
		path_in (str): Path to the VCF file containing the data.
		path_out (str): Output file, where the result will be written.
		populations (list): List of population labels for the samples in the VCF file, *in the same order*.
		diploid (bool): If the samples are diploid.
	"""

	num_loci = _count_loci(path_in)
	temp_dir = os.path.join(os.path.dirname(path_out), random_string(12))

	identifiers = _get_identifiers(path_in)

	if len(identifiers) != len(np.unique(identifiers)):
		raise LoadingError('Sample identifiers must be unique.')
	if len(populations) != len(identifiers):
		raise ValueError('Mismatch between the number of samples and populations labels.')

	print('Opened VCF file with {0} samples and {1} loci.'.format(len(identifiers), num_loci))

	if not os.path.exists(temp_dir):
		os.makedirs(temp_dir)

	temp_files_right = [os.path.join(temp_dir, sample+'_A') for sample in identifiers]
	temp_files_left = [os.path.join(temp_dir, sample+'_B') for sample in identifiers]

	temp_genotypes_right = ['' for _ in identifiers]
	temp_genotypes_left = ['' for _ in identifiers]

	temp_count = 0

	with open(path_in) as fin:
		with tqdm(total=num_loci, desc='Transposing data...') as progress:
			while True:
				line = fin.readline()

				if not line:
					break

				if line[0] != '#':
					temp_count += 1
					progress.update(1)

					line = line.split()

					for sample_index, genotype in enumerate(line[_GENOTYPE_START_COL:]):

						temp_genotypes_right[sample_index] += genotype[0]
						if diploid:
							temp_genotypes_left[sample_index] += genotype[2]

						if temp_count % _LINE_LEN == 0:
							temp_genotypes_right[sample_index] += '\n'
							if diploid:
								temp_genotypes_left[sample_index] += '\n'

					if temp_count % _BUFFER_LEN == 0 and temp_count > 0:
						temp_files_right, temp_genotypes_left = _flush(temp_files_right, temp_files_left,
																	   temp_genotypes_right, temp_genotypes_left)

			_flush(temp_files_right, temp_files_left, temp_genotypes_right, temp_genotypes_left)

	with tqdm(total=len(identifiers), desc='Merging transposed data...') as progress:
		with open(path_out, 'w+') as fout:
			for file_r, file_l, iden, pop in zip(temp_files_right, temp_files_left, identifiers, populations):

				_write_line(file_r, fout, iden, pop)
				if diploid:
					_write_line(file_l, fout, iden, pop)
				progress.update(1)

	for file in temp_files_right:
		os.unlink(file)
	for file in temp_files_left:
		os.unlink(file)

	os.rmdir(temp_dir)

if __name__ == '__main__':
	pass