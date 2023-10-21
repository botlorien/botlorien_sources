import os
from supabase import create_client, Client

class Supabase():
    def __init__(self):
        self.url = "https://ebvsmcekeiyilmlnbgpc.supabase.co"
        self.key = os.getenv('supabase')
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
    sup.generate_url_to_download()
    sup.list_files()