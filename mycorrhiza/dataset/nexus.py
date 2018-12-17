import os
import numpy as np
import re


def writeHeader(f, name, numTaxa):
	f.write('#nexus\n')
	f.write('[' + str(name) + ']\n')
	f.write('BEGIN Taxa;\n')
	f.write('DIMENSIONS ntax=' + str(numTaxa) + ';\n')
	f.write('END;\n\n')


def writeDistancesBlock(f, distances, taxa):
	f.write('BEGIN Distances;\n')
	f.write('DIMENSIONS ntax=' + str(distances.shape[0]) + ';\n')
	f.write('FORMAT labels=left diagonal triangle=both;\n')
	writeMatrixWithLabels(f, distances, taxa)
	f.write('END; [Distances]\n')

'''
def writeCharactersBlock(f, characters, taxa):
	f.write('BEGIN Characters;\n')
	f.write('DIMENSIONS nchar=' + str(len(characters[0])) + ';\n')
	f.write('FORMAT datatype=dna missing=N transpose=no interleave=no;\n')
	writeMatrix(f, characters, taxa)
	f.write('END; [Characters]\n')
'''

def start_characters_block(f, num_loci):
	f.write('BEGIN Characters;\n')
	f.write('DIMENSIONS nchar=' + str(num_loci) + ';\n')
	f.write('FORMAT datatype=dna missing=N transpose=no interleave=no;\n')
	f.write('MATRIX\n')


def write_characters_line(f, sample_idx, sample_id, line):
	f.write('[' + str(sample_idx + 1) + ']\t' + sample_id + '\t' + ''.join([str(d) for d in line]).strip() + '\n')


def end_block(f):
	f.write('\n;\n')
	f.write('END;\n')


def writeMatrixWithLabels(f, matrix, taxa):
	f.write('MATRIX\n')
	for i, (taxon, row) in enumerate(zip(taxa, matrix)):
		regex = re.compile('[^a-zA-Z]')
		f.write('[' + regex.sub('', taxon) + str(i) + ']\t' + taxon + ''.join(['\t' + str(d) for d in row]) + '\n')
	f.write('\n;\n')


def writeMatrix(f, matrix, taxa):
	f.write('MATRIX\n')
	for i, row in enumerate(matrix):
		f.write(taxa[i] + '\t' + ''.join(row) + '\n')
	f.write('\n;\n')


def writeFooter(f, commands, update=True, export=True, quit=True):
	f.write('BEGIN st_Assumptions;\n')
	for c in commands:
		f.write('\t' + c + ';\n')
	f.write('END; [st_Assumptions]\n\n')
	f.write('begin SplitsTree;\n')
	if update: f.write('\tUPDATE;\n')
	if export: f.write('\tEXPORT FILE=' + os.path.abspath(f.name) + ' REPLACE=yes;\n')
	if quit: f.write('\tQUIT;\n')
	f.write('end;\n')


def readDistancesBlock(filename):
	distMatrix = []

	with open(filename + '.nex', 'r') as f:
		begin = False
		matrix = False
		done = False

		for i, row in enumerate(f.readlines()):
			if begin and matrix and not done:
				if len(row) <= 5:
					done = True
				else:
					parts = row.split()
					row = np.array(parts[2:])
					distMatrix.append(row.astype(float))
			elif "BEGIN Distances;" in row:
				begin = True
			elif begin and 'MATRIX' in row and not done:
				matrix = True

	return np.array(distMatrix)

def readSplitsBlock(filename):
	splitsMatrix = []
	ordering = []
	weights = []

	with open(os.path.join(filename), 'r') as f:
		lines = f.readlines()

		splits = False
		number = 0
		matrix = False
		done = False

		for i, row in enumerate(lines):
			row = str(row)
			if splits and row[:5] == 'CYCLE' and not done:
				ordering = np.array(row[5:].split())
				ordering[-1] = ordering[-1].replace(';', '')
				ordering = ordering.astype(int)
			if splits and matrix and not done:
				if len(row) <= 5:
					done = True
				else:
					parts = row.split()
					weights.append(float(parts[2]))
					row = np.array(parts[3:])
					row[-1] = row[-1].replace(',', '')

					row = row.astype(int) - 1
					binary = np.array([0] * number)
					binary[row] = 1
					splitsMatrix.append(binary)
			elif row[:13] == 'BEGIN Splits;':
				splits = True
			elif splits and row[:10] == 'DIMENSIONS' and not done:
				digits = row.split()[1].split('=')[1].replace(';', '')
				number = int(digits)
			elif splits and row[:6] == 'MATRIX' and not done:
				matrix = True

	ordering = [o - 1 for o in ordering]
	splitsMatrix = np.array(splitsMatrix)

	return splitsMatrix, np.array(weights), np.array(ordering)


