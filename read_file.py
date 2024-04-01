import pandas as pd
from time import sleep


def mt_code_read(path: str) -> tuple:
	program = {}
	logs = ''
	file_type = path.split('.')[-1]
	if file_type == 'xlsx':
		data = pd.read_excel(path)
	elif file_type == 'csv':
		data = pd.read_csv(path)
	else:
		logs = 'Неправильный формат файла. Поддерживаемые форматы: .xlsx/.csv'
		return program, logs

	try:
		df = pd.DataFrame(data, columns = ['A', 'Q', 'φ', 'ψ', 'H'])
		if df.isnull().values.any():
			logs = 'Неправильно заполнена таблица, либо пустые значения в ячейках. Заполняйте строго по шаблону, прикрепленному к разделу на контесте'
			return program, logs

		for line in df.iloc:
			if line['Q'] not in program:
				program[line['Q']] = [(0, 'S', line['Q']), (1, 'S', line['Q'])]

			program[line['Q']][int(line['A'])] = (int(line['ψ']), line['H'].upper(), line['φ'])
			if line['φ'] not in program:
				program[line['φ']] = [(0, 'S', line['φ']), (1, 'S', line['φ'])]
		logs = 'Файл успешно считан\n'
		move_alphabet = set(df['H'].values.tolist())
		if abs(max(df['A'].values.tolist())) > 1 or abs(max(df['ψ'].values.tolist())) > 1:
			logs = 'Входной и выходной алфавиты Машины Тьюринга могут состоять только из 0 и 1'
			program = {}

		elif move_alphabet.union({'L','R','S'}) != {'L', 'R', 'S'}:
			logs = 'Для перемещения по ленте можно использовать только нижеследующие символы:\nL - налево\nR - направо\nS - остановка'
			program = {}

	except Exception as e:
		if 'invalid literal for int() with base 10:' in str(e):
			logs = 'Перепутаны столбцы состояний и значений Машины Тьюринга'
		elif "'int' object has no attribute 'upper'" in str(e):
			logs = 'Для перемещения по ленте можно использовать только нижеследующие символы:\nL - налево\nR - направо\nS - остановка'
		elif 'max() arg is an empty sequence' in str(e):
			logs = 'Подана пустая таблица'
		else:
			logs = str(e)

		program = {}

	return program, logs