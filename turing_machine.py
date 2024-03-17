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
    self.time_limit = 0

  def test(self, submission_file: str, problem: str, criteria: list[int], time_limit: int, test: list[int] = None) -> tuple:
    self.program = mt_code_read(submission_file)
    self.start_state = list(self.program.keys())[0]
    self.function = problem.replace('div', '//').replace('mod', '%')
    self.variables_names = sorted(list(set(re.findall("x[0-9]+", problem))))
    self.variables_num = len(self.variables_names)
    self.time_limit = time_limit
    logs = ''

    func = self.function
    if test is None:
      correct_answers = 0
      log_flag = ('log' in self.function)*2
      for x in range(0 + log_flag, 100 + log_flag):
        values = [abs(x + randint(-5, 5)) + log_flag for x in range(self.variables_num)]
        values[0] = x
        mt_tape = '0'.join(j for j in [''.join(str(1) for n in range(j+1)) for j in values])
        tape = self.run(list(mt_tape))
        MT_value = sum([int(j) for j in tape])-1
        func_value = self.calculate(values)
        if MT_value != func_value:
          logs += f'Fail! Function value: {func_value}, Turing Machine value: {MT_value}, variables values: [{values}]\n'

        else:
          correct_answers += 1

      logs += f'Correct answers: {correct_answers}'
      mark = self.get_mark(correct_answers, criteria)

      return mark, logs

    else:
      if len(test) != self.variables_num:
        raise Exception('The number of variables does not match the number of values')

      mt_tape = '0'.join(j for j in [''.join(str(1) for n in range(j+1)) for j in test])
      tape = self.run(list(mt_tape))
      MT_value = sum([int(j) for j in tape])-1
      func_value = self.calculate(test)
      mark = {True: 5, False: 2}[MT_value == func_value]
      if mark == 2:
        logs = f'Fail! Function value: {func_value}, Turing Machine value: {MT_value}'

      else:
        logs = f'Success! Function value: {func_value}, Turing Machine value: {MT_value}'  

      return mark, logs



  def calculate(self, values: list[int]) -> int:
    func = self.function
    for var in range(self.variables_num):
      func = func.replace(self.variables_names[var], str(values[var]))

    return int(eval(func))

  def get_mark(self, correct_answers: int, criteria: list[int]) -> int:
    if correct_answers >= criteria[0]:
      return 5
    elif correct_answers >= criteria[1]:
      return 4
    elif correct_answers >= criteria[2]:
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
        raise Exception('Program execution time exceeded')

    return self.tape

  def tape_builder(self, current_index: int) -> int:
    while current_index >= len(self.tape):
      self.tape += '0'

    while current_index < 0:
      self.tape = ['0'] + self.tape
      current_index += 1

    return current_index