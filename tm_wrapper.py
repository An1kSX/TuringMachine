from pathlib import Path
import pandas as pd
from native import tm_test
import ctypes



class TuringMachine:
	@staticmethod
	def _xlsx_to_csv(xlsx_path: Path) -> Path:
		csv_path = xlsx_path.with_suffix('.csv')
		df = pd.read_excel(xlsx_path, sheet_name=0, header=None)
		df.to_csv(csv_path, index=False, header=False, sep=';', encoding="utf-8-sig")

		xlsx_path.unlink()

		return csv_path

	def test(self, submission_file: str, problem: str, criteria: list[int], time_limit: int = 30, launch_args: int = 1):
		path = Path(submission_file)
		if path.suffix.lower() in {'.xlsx', '.xls'}:
			path = self._xlsx_to_csv(path)

		criteria_str = ",".join(map(str, criteria)).encode("utf‑8")
		path = str(path).encode("utf‑8")
		problem = problem.encode("utf‑8")
		log_buf = ctypes.create_string_buffer(16 * 1024)

		mark = tm_test(path, problem, criteria_str, time_limit, launch_args, log_buf, ctypes.sizeof(log_buf))

		logs = logs = log_buf.value.decode("utf-8", errors="replace")

		return mark, logs