# import the tasks modules here!
import logging
import tasks as ts
from interface import Interface
from ssw import SswRequest
from datahandler import Handler

hd = Handler()


class Tasks:

    def __init__(self, app):
        self.app = app
        self.app.set_bot_name('Bot_name')
        self.app.set_bot_description(
            'This bot do this')
        self.app.set_bot_version('1.0.0')
        self.app.init_bot()
        self.user = ''

        # init here every task result as needle
        self.task1_result = None
        self.task2_result = None

    @hd.time_out(3)
    def init_credentials(self):
        ssw = SswRequest()
        ssw.init_browser()
        ssw.login()
        self.user = ssw.credentials[2]
        self.app.set_user(self.user)

    # copy this structure for every task of the bot
    def task1(self):
        task_name = 'task1'
        task_description = 'task description here!'
        task_function = ts

        self.app.set_task(task_name, task_description)
        self.task1_result = self.app.execute_bot_task(task_function)

    def task2(self):
        task_name = 'task2'
        task_description = 'task description here!'
        task_function = ts

        self.app.set_task(task_name, task_description)
        self.task2_result = self.app.execute_bot_task(task_function)




def main_ui(app):
    while True:
        tasks = Tasks(app)
        tasks.init_credentials()
        ui = Interface(user=tasks.user)
        buttons_name = ['task1', 'task2']
        buttons_func = [tasks.task1, tasks.task2]
        ui.ui(buttons_name, buttons_func)


def main(app):
    tasks = Tasks(app)
    tasks.init_credentials()
    tasks.task1()
    tasks.task2()
    # ... another task here!


if __name__ == '__main__':
    pass
