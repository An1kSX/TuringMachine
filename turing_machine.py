import time
import re
from math import log
from random import randint
from read_file import mt_code_read


class TuringMachine:
    def __init__(self):
        self.program = None
        self.tape = None
        self.start_state = None
        self.movement_encode = {
                               'R': +1,
                               'L': -1,
                               'S': 0
                               }
        self.variables_num = 0
        self.function = None
        self.variables_names = None
        self.time_limit = 10
        self.start_time = 0
        self.logs = ''

    def test(self, submission_file: str, problem: str, criteria: list[int],
             time_limit: int, test: list[int] | int) -> tuple:
        self.program, self.logs = mt_code_read(submission_file)
        if len(self.program) == 0:
            return 2, self.logs

        self.start_state = list(self.program.keys())[0]
        self.function = problem.replace('div', '//').replace('mod', '%')
        self.function = self.function.replace('^', '**')
        variables_in_problem = re.findall("x[0-9]+", problem)
        self.variables_names = sorted(list(set(variables_in_problem)))
        self.variables_num = len(self.variables_names)
        self.time_limit = time_limit

        correct_answers = 0
        log_flag = ('log' in self.function)

        if type(test) is int:
            mark_multiplier = 100/test
            self.start_time = time.time()
            for x in range(0 + log_flag, test + log_flag):
                values = [abs(x + randint(-5, 5)) + log_flag for y in range(self.variables_num)]
                if self.variables_num > 0:
                    values[0] = x

                mt_tape = '0'.join(j for j in [''.join(str(1) for n in range(j+1)) for j in values])

                result_tape = self.run(list(mt_tape))
                if result_tape is None:
                    break

                MT_value = sum([int(j) for j in result_tape])-1
                func_value = self.calculate(values)

                if MT_value != func_value:
                    self.logs += (f'Ошибка! Значение функции: {func_value},' +
                                  f' Значение Машины Тьюринга: {MT_value},' +
                                  f' Значения переменных: {values}\n'
                                  )

                else:
                    self.logs += (f'Успешно! Значение функции: {func_value},' +
                                  f' Значение Машины Тьюринга: {MT_value},' +
                                  f' Значения переменных: {values}\n'
                                  )
                    correct_answers += 1

            self.logs += f'Количество правильных ответов: {correct_answers}'
            mark = self.get_mark(correct_answers, criteria, mark_multiplier)

            return mark, self.logs

        else:
            if len(test) != self.variables_num:
                raise Exception('Количество переменных не совпадает с' +
                                ' количеством поданных значений. Переменные' +
                                ' необходимо называть: x1, x2, ..., xn'
                                )

            mt_tape = '0'.join(j for j in [''.join(str(1) for n in range(j+1)) for j in test])

            result_tape = self.run(list(mt_tape))
            MT_value = sum([int(j) for j in result_tape])-1
            func_value = self.calculate(test)
            mark = {True: 5, False: 2}[MT_value == func_value]
            if mark == 2:
                self.logs += (f'Ошибка! Значение функции: {func_value},' +
                              f' Значение Машины Тьюринга: {MT_value}'
                              )

            else:
                self.logs += (f'Успешно! Значение функции: {func_value},' +
                              f' Значение Машины Тьюринга: {MT_value}'
                              )

            return mark, self.logs

    def calculate(self, values: list[int]) -> int:
        func = self.function
        for var in range(self.variables_num):
            func = func.replace(self.variables_names[var], str(values[var]))

        try:
            func_value = int(eval(func))

        except Exception:
            raise Exception('Неправильная запись функции.\n' +
                            'Переменные следует называть: x1, x2, ..., xn\n' +
                            'Умножение: x1*4 / x1*x2\n' +
                            'Возведение в степень: x1^2 / x1^x2\n' +
                            'Сложение: x1+2 / x1+x2\n' +
                            'Остаток от деления: x1mod7 / x1modx2\n' +
                            'Деление без остатка: x1div3 / x1divx2\n' +
                            'Логарифм: log(x1, 2) / log(x1, x2).' +
                            ' Основание логарифма - второй аргумент'
                            )

        return func_value

    def get_mark(self, correct_answers: int, criteria: list[int],
                 mark_multiplier: int) -> int:
        score = correct_answers*mark_multiplier

        if score >= criteria[0]:
            return 5
        elif score >= criteria[1]:
            return 4
        elif score >= criteria[2]:
            return 3
        else:
            return 2

    def run(self, tape: list) -> list:
        self.tape = tape
        change_to = 0
        move_to = 1
        new_state = 2
        current_index = 0
        current_state = self.start_state

        while True:
            if (current_index >= len(self.tape) or current_index < 0):
                current_index = self.tape_builder(current_index)

            rows = self.program[current_state]
            current_row = rows[int(self.tape[current_index])]
            prev = self.tape[current_index]
            self.tape[current_index] = str(current_row[change_to])

            if (not self.movement_encode[current_row[move_to]] and
                    current_state == current_row[new_state] and
                    prev == str(current_row[change_to])):
                break

            current_index += self.movement_encode[current_row[move_to]]
            current_state = current_row[new_state]

            working_time = time.time() - self.start_time
            if working_time > self.time_limit:
                self.logs += 'Превышено время работы программы\n'
                return None

        return self.tape

    def tape_builder(self, current_index: int) -> int:
        while current_index >= len(self.tape):
            self.tape += '0'

        while current_index < 0:
            self.tape = ['0'] + self.tape
            current_index += 1

        return current_index
