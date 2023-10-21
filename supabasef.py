import os
from supabase import create_client, Client

class Supabase():
    def __init__(self):
        self.url = "https://ebvsmcekeiyilmlnbgpc.supabase.co"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVidnNtY2VrZWl5aWxtbG5iZ3BjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5MzQwODk2NCwiZXhwIjoyMDA4OTg0OTY0fQ.O96y28NqaC4XfW_PZrn6lhnoNNZayZg5gGWUBEMlBpc"
        self.sup = create_client(self.url, self.key)

    def create_bucket(self,name):
        res = self.sup.storage.create_bucket(name,'public')
        print(res)

    def upload_file(self,source):
        with open(source, 'rb') as f:
            res = self.sup.storage.from_('Teste_files').upload('teste2.xlsx', f)
            print(res)

    def generate_url_to_download(self):
        res = self.sup.storage.from_('Teste_files').get_public_url('teste2.xlsx')
        print(res)

    def list_files(self):
        res = self.sup.storage.from_('Teste_files').list()
        print(res)


if __name__=='__main__':
    sup = Supabase()
    #sup.create_bucket('Teste_files')
    file_=r'C:\Users\06213\OneDrive\GitHub\CARVALIMA\priority_classes\base\JohnDeere.xlsx'
    #sup.upload_file(file_)
    sup.generate_url_to_download()
    sup.list_files()