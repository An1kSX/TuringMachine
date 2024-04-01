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
    self.logs = ''

  def test(self, submission_file: str, problem: str, criteria: list[int], time_limit: int, test: list[int] = None, chapter: int = None) -> tuple:
    self.program, self.logs = mt_code_read(submission_file)
    if len(self.program) == 0:
      return 2, self.logs
    self.start_state = list(self.program.keys())[0]
    self.function = problem.replace('div', '//').replace('mod', '%').replace('^', '**')
    self.variables_names = sorted(list(set(re.findall("x[0-9]+", problem))))
    self.variables_num = len(self.variables_names)
    self.time_limit = time_limit

    func = self.function
    if test is None:
      if chapter is None or chapter not in [1,2,3]:
        raise Exception('Нужно указать один из трех разделов, к которому относится задача')

      tests_count = {1: 100, 2: 50, 3:25}[chapter]                     #определение количества тестов по разделу задачи
      mark_multiplier = {1: 1, 2: 2, 3: 4}[chapter]                             #определение количества баллов за правильный ответ исходя из раздела задачи
      correct_answers = 0
      log_flag = ('log' in self.function)
      for x in range(0 + log_flag, tests_count + log_flag):
        values = [abs(x + randint(-5, 5)) + log_flag for y in range(self.variables_num)]
        if self.variables_num > 0:
          values[0] = x
        mt_tape = '0'.join(j for j in [''.join(str(1) for n in range(j+1)) for j in values])
        tape = self.run(list(mt_tape))
        if tape is None:
          self.logs += 'Превышено время ожидания работы программы\n'
          break
        MT_value = sum([int(j) for j in tape])-1
        func_value = self.calculate(values)

        if MT_value != func_value:
          self.logs += f'Ошибка! Значение функции: {func_value}, Значение Машины Тьюринга: {MT_value}, значения переменных: {values}\n'

        else:
          self.logs += f'Успешно! Значение функции: {func_value}, Значение Машины Тьюринга: {MT_value}, значения переменных: {values}\n'
          correct_answers += 1

      self.logs += f'Количество правильных ответов: {correct_answers}'
      mark = self.get_mark(correct_answers, criteria, mark_multiplier)

      return mark, self.logs

    else:
      if len(test) != self.variables_num:
        raise Exception('Количество переменных не совпадает с количеством поданных значений.\nПеременные необходимо называть: x1, x2, ..., xn')

      mt_tape = '0'.join(j for j in [''.join(str(1) for n in range(j+1)) for j in test])
      tape = self.run(list(mt_tape))                                  
      MT_value = sum([int(j) for j in tape])-1
      func_value = self.calculate(test)
      mark = {True: 5, False: 2}[MT_value == func_value]
      if mark == 2:
        self.logs += f'Ошибка! Значение функции: {func_value}, Значение Машины Тьюринга: {MT_value}'

      else:
        self.logs += f'Успешно! Значение функции: {func_value}, Значение Машины Тьюринга: {MT_value}'  

      return mark, logs



  def calculate(self, values: list[int]) -> int:
    func = self.function
    for var in range(self.variables_num):
      func = func.replace(self.variables_names[var], str(values[var]))

    try:
      func_value = int(eval(func))
    except:
      raise Exception('Неправильная запись функции.\nПеременные следует называть: x1, x2, ..., xn\nУмножение: x1*4 / x1*x2\nВозведение в степень: x1^2 / x1^x2\nСложение: x1+2 / x1+x2\nОстаток от деления: x1mod7 / x1modx2\nДеление без остатка: x1div3 / x1divx2\nЛогарифм: log(x1, 2) / log(x1, x2). Основание логарифма - второй аргумент')

    return int(eval(func))

  def get_mark(self, correct_answers: int, criteria: list[int], mark_multiplier: int) -> int:
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
    CHANGE_TO = 0
    MOVE_TO = 1
    NEW_STATE = 2
    current_index = 0
    working_time = 0
    start_time = time.time()
    current_state = self.start_state

    while True:
      if current_index >= len(self.tape) or current_index < 0:
        current_index = self.tape_builder(current_index)

      rows = self.program[current_state]
      current_row = rows[int(self.tape[current_index])]
      prev = self.tape[current_index]
      self.tape[current_index] = str(current_row[CHANGE_TO])

      if (not self.movement_encode[current_row[MOVE_TO]]) and (current_state == current_row[NEW_STATE]) and (prev == str(current_row[CHANGE_TO])):
        break

      current_index += self.movement_encode[current_row[MOVE_TO]] 
      current_state = current_row[NEW_STATE]

      working_time = time.time() - start_time
      if working_time > self.time_limit:
        self.logs += 'Превышено время работы программы'
        return None

    return self.tape

  def tape_builder(self, current_index: int) -> int:
    while current_index >= len(self.tape):
      self.tape += '0'

    while current_index < 0:
      self.tape = ['0'] + self.tape
      current_index += 1

    return current_index