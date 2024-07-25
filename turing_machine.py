import re
import time
import math

from simpleeval import simple_eval
from random import randint
from typing import Union

from read_file import mt_code_read

RE_VARS = re.compile(r"x[0-9]+")
RE_LOGARITHM = re.compile(r"log\d+[(]\d+[)]")


class TuringMachine:
    """Данный класс предназначен для проверки корректности кода машиный Тьюринга"""
    def __init__(self):
        self.program = None
        self.tape = None
        self.start_state = None
        self.movement_encode = {'R': +1, 'L': -1, 'S': 0}
        self.variables_num = 0
        self.function = None
        self.variables_names = None
        self.time_limit = 1
        self.logs = ''

    def test(self, submission_file: str, problem: str, criteria: list[int],
             test: Union[list[int], int], observer=None) -> tuple:
        self.program, self.logs = mt_code_read(submission_file)
        if len(self.program) == 0:
            return 2, self.logs
        self.start_state = list(self.program.keys())[0]
        self.function = problem.replace('div', '//').replace('mod', '%')
        self.function = self.function.replace('^', '**')
        variables_in_problem = re.findall(RE_VARS, problem)
        self.variables_names = sorted(list(set(variables_in_problem)))
        self.variables_num = len(self.variables_names)
        if type(test) is int:
            correct_answers = 0
            log_flag = ('log' in self.function)
            combinations = self.generate_combinations(test)
            mark_multiplier = 100 / len(combinations)
            for combination in combinations:
                if observer is not None:
                    observer.set_progress('Проверяем', x, test)
                values = [x + log_flag for x in combination]
                mt_tape = '0'.join(j for j in [''.join(str(1) for _ in range(j + 1)) for j in values])
                ok = self.run(list(mt_tape))
                if not ok:
                    self.logs += f"Значения переменных: {values}\n"
                    continue
                func_value = self.calculate(values, log_flag)
                MT_value = sum([int(j) for j in self.tape]) - 1
                if MT_value != func_value:
                    self.logs += (f'Ошибка! Значение функции: {func_value}, Значение Машины Тьюринга: {MT_value}, '
                                  f'Значения переменных: {values}\n')
                else:
                    self.logs += (f'Успешно! Значение функции: {func_value}, Значение Машины Тьюринга: {MT_value}, '
                                  f'Значения переменных: {values}\n')
                    correct_answers += 1
            self.logs += f'Количество правильных ответов: {correct_answers}'
            mark = self.get_mark(correct_answers, criteria, mark_multiplier)
            return mark, self.logs
            
        else:
            if len(test) != self.variables_num:
                raise Exception('Количество переменных не совпадает с количеством поданных значений. Переменные '
                                'необходимо называть: x1, x2, ..., xn')
            mt_tape = '0'.join(j for j in [''.join(str(1) for _ in range(j + 1)) for j in test])
            ok = self.run(list(mt_tape))
            if not ok:
                self.logs += f"Значения переменных: {test}"
            MT_value = sum([int(j) for j in self.tape]) - 1
            func_value = self.calculate(test, 0)
            mark = {True: 5, False: 2}[MT_value == func_value]
            if mark == 2 and ok:
                self.logs += f'Ошибка! Значение функции: {func_value}, Значение Машины Тьюринга: {MT_value}'
            elif mark > 2:
                self.logs += f'Успешно! Значение функции: {func_value}, Значение Машины Тьюринга: {MT_value}'
            return mark, self.logs

    def calculate(self, values: list[int], log_flag: bool) -> int:
        func = self.function
        for var in range(self.variables_num):
            func = func.replace(self.variables_names[var], str(values[var]))

        if log_flag:
            logarithms = re.findall(RE_LOGARITHM, func)
            for logarithm in logarithms:
                log_base = logarithm.split('(')
                log_base = int(log_base[0][3:])
                log_a = logarithm.replace(f"log{log_base}", "log")
                log_b = f'log({log_base})'
                func = func.replace(logarithm, f'{log_a} / {log_b}')

        try:
            func_value = int(simple_eval(func, functions={"log": lambda x: math.log(x)}))
        except Exception:
            raise Exception('Неправильная запись функции.\n'
                            'Переменные следует называть: x1, x2, ..., xn\n'
                            'Умножение: x1*4 / x1*x2\n'
                            'Возведение в степень: x1^2 / x1^x2\n'
                            'Сложение: x1+2 / x1+x2\n'
                            'Остаток от деления: x1mod7 / x1modx2\n'
                            'Деление без остатка: x1div3 / x1divx2\n'
                            'Логарифм: log2(x1) / logx2(x1). '
                            'Основание логарифма - число сразу после log')
        return func_value

    def get_mark(self, correct_answers: int, criteria: list[int], mark_multiplier: float) -> int:
        score = correct_answers * mark_multiplier
        if score >= criteria[0]:
            return 5
        elif score >= criteria[1]:
            return 4
        elif score >= criteria[2]:
            return 3
        else:
            return 2

    def run(self, tape: list) -> bool:
        self.tape = tape
        change_to = 0
        move_to = 1
        new_state = 2
        current_index = 0
        current_state = self.start_state
        start_time = time.time()
        while True:
            if current_index >= len(self.tape) or current_index < 0:
                current_index = self.tape_builder(current_index)
            rows = self.program[current_state]
            current_row = rows[int(self.tape[current_index])]
            prev = self.tape[current_index]
            self.tape[current_index] = str(current_row[change_to])
            if (not self.movement_encode[current_row[move_to]]
                    and current_state == current_row[new_state]
                    and prev == str(current_row[change_to])):
                break
            current_index += self.movement_encode[current_row[move_to]]
            current_state = current_row[new_state]
            working_time = time.time() - start_time
            if working_time > self.time_limit:
                self.logs += 'Превышено время работы программы! '
                return False

        return True

    def tape_builder(self, current_index: int) -> int:
        while current_index >= len(self.tape):
            self.tape += '0'
        while current_index < 0:
            self.tape = ['0'] + self.tape
            current_index += 1
        return current_index

    def generate_combinations(self, max_num: int):
        def backtrack(current_combination, index):
            if len(combinations) >= 30:
                return

            if index == self.variables_num:
                combinations.append(tuple(current_combination))
                return

            for value in range(max_num + 1):
                current_combination.append(value)
                backtrack(current_combination, index + 1)
                current_combination.pop()

        combinations = []
        backtrack([], 0)

        return combinations
