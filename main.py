from turing_machine import TuringMachine


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
		'4*x1+x2': 400
		}

for test in tests:
	file_name = test.replace("*", "")

	print(f"Тест: {test}")

	mark, logs = mt.test(
		submission_file=r"C:\Users\Anik\Desktop\diplom2\%s.csv" % (file_name),
		problem=test,
		criteria=[98, 96, 95],
		time_limit=30,
		launch_args=tests[test]
		)

	if mark < 5:
		print(f"{logs}\nОценка: {mark}")

	else:
		print("OK")
