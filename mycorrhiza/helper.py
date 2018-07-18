import random
import string


def random_string(N: int):
	return ''.join([random.choice(string.ascii_uppercase + string.digits) for _ in range(N)])


def file_to_list(path_in):
	data = []
	with open(path_in) as fin:
		for line in fin:
			line = line.strip()
			if len(line) != 0:
				data.append(line)

	return data

