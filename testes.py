########### Testes ##############################
import os
import time


def task1():
    from datahandler import Handler
    from database import Postgresql, Sqlite
    hd = Handler()
    db = Sqlite()

    df = hd.import_file('files')  # ,number_file=1,skiprows=1
    print(df)
    time.sleep(1)
    df = hd.clear_table(df)
    print(df)
    time.sleep(1)
    df = hd.convert_table_types(df, dtypes={'datetime': ['prazo', 'emissao']})
    print(df)
    time.sleep(1)

    db.to_sqlite(df, 'teste_new_class2')
    return os.listdir('files')

def task2():
    from datahandler import Handler
    hd = Handler()
    df = hd.import_file('files',number_file='1',skiprows=1)  #
    print(df)
    return df

def testing_insert_on_logbots():
    from botsdatabase import TableBots,TaskTable,TaskResults
    table_bot = TableBots()
    task_table = TaskTable()
    task_result = TaskResults()

    # register bot
    table_bot.init_values('bot_carvalima4','Bot to perform bussiness operations')
    table_bot.show_values()
    table_bot.register_bot()

    # register task
    task_table.init_values(table_bot.bot_id,'atividade2','perform web scraping with selenium')
    task_table.show_values()
    task_table.register_task()

    # initializing new result from task
    task_result.init_values(task_table.task_id, os.getcwd(), 'botcvl', '1.0.0')
    task_result.show_values()

    # opening the new task result
    task_result.open_task()
    time.sleep(10)

    task_result.end_task(True,'Resultado','Erro')
    task_result.show_values()


def teste_chrome_download():
    from ssw import SswRequest

    ssw = SswRequest()
    ssw.chromedriver_install()



if __name__ == '__main__':
    teste_chrome_download()

