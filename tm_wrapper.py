from pathlib import Path
import pandas as pd
import tm_interface


class TuringMachine:
	def __init__(self):
		self._tm = tm_interface.TuringMachine()

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

		return self._tm.test(str(path), problem, criteria, time_limit, launch_args)