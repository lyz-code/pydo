from pydo.manager import TaskManager

import unittest


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.tm = TaskManager()
