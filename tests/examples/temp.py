cl = {}

with open('classes.tsv') as fin:
	for line in fin:
		line = line.strip().split()
		cl[line[0]]	= line[1]

with open('out', 'w+') as fout:
	with open('gipsy.myc') as fin:
		for line in fin:
			sep = line.strip().split()
			if sep[0] in cl:

				fout.write('{0} {1} {2} {3}\n'.format(sep[0], '0', cl[sep[0]], ' '.join(sep[1:])))