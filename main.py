from turing_machine import TuringMachine
import os


mt = TuringMachine()

tests = {
		'x1+3*x2': 400,
		'x1*x2 + 2': 100,
		'x1div5 + x2 + 7': 400,
		'2*x1 + 4*x2 + 5*x3': 400,
		'x1^2 + x2 + 11': 50,
		'10*x1 + x2 + 2': 400,
		'x1*x2 + 6': 100,
		'x1mod2 + x2 + 7': 400,
		'x1+2*x2+3': 400,
		'4*x1+x2': 400,
		'x1^2 + x2 + 4': 50,
		'x1 + x2 + 8': 400,
		'x1 + 7*x2': 400
		}

for test in tests:
	dir_path = os.path.dirname(os.path.realpath(__file__))

	file_name = test.replace("*", "")
	submission_path = os.path.join(dir_path, "tests", f"{file_name}.csv")

	print(f"Тест: {test}")
	print(f'Рабочая директория: {dir_path}')
	print(f'Директория файла: {submission_path}')

	mark, logs = mt.test(
		submission_file=submission_path,
		problem=test,
		criteria=[98, 96, 95],
		time_limit=30,
		launch_args=tests[test]
		)

	if mark < 5:
		print(f"Результат: {logs}\nОценка: {mark}\n")

	else:
		print("Результат: OK\n")
