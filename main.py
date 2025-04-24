from tm_wrapper import TuringMachine


mt = TuringMachine()

mark, logs = mt.test(
	submission_file=r"C:\Users\Anik\Desktop\diplom2\test.csv",
	problem="5*(x1 + 3)^2",
	criteria=[85, 65, 55],
	time_limit=30,
	launch_args=50
	)

print(f"{logs}\nОценка: {mark}")