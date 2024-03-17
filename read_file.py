import pandas as pd
from time import sleep


def mt_code_read(path: str) -> dict:
	program = {}
	file_type = path.split('.')[-1]
	if file_type == 'xlsx':
		data = pd.read_excel(path)
	elif file_type == 'csv':
		data = pd.read_csv(path)
	else:
		raise Exception("Wrong file type")

	df = pd.DataFrame(data, columns = ['A', 'Q', 'φ', 'ψ', 'H'])
	for line in df.iloc:
		if line['Q'] not in program:
			program[line['Q']] = [(0, 'S', line['Q']), (1, 'S', line['Q'])]

		program[line['Q']][int(line['A'])] = (int(line['ψ']), line['H'].upper(), line['φ'])
		if line['φ'] not in program:
			program[line['φ']] = [(0, 'S', line['φ']), (1, 'S', line['φ'])]

	return program



