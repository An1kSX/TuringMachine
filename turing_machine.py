from pathlib import Path
import pandas as pd
from .native import tm_test
import ctypes



class TuringMachine:
	@staticmethod
	def _xlsx_to_csv(xlsx_path):
		csv_path = xlsx_path.with_suffix('.csv')
		df = pd.read_excel(xlsx_path, sheet_name=0, header=None)
		df.to_csv(csv_path, index=False, header=False, sep=';', encoding="utf-8-sig")

		return csv_path

	def test(self, submission_file, problem, criteria, time_limit = 30, launch_args = 1, observer=None):
		if not launch_args:
			launch_args = 1
		try:
			launch_args = int(launch_args)
		except:
			raise ValueError("Аргумент запуска должент быть типа int")
		
		path = Path(submission_file)

		flag = False
		if path.suffix.lower() in {'.xlsx', '.xls'}:
			path = self._xlsx_to_csv(path)
			flag = True

		criteria_str = ",".join(map(str, criteria)).encode("utf-8")
		path_str = str(path).encode("utf-8")
		problem = problem.encode("utf-8")
		log_buf = ctypes.create_string_buffer(256 * 1024)

		mark = tm_test(path_str, problem, criteria_str, time_limit, launch_args, log_buf, ctypes.sizeof(log_buf))

		logs = logs = log_buf.value.decode("utf-8", errors="replace")

		if flag:
			path.unlink()

		return mark, logs
