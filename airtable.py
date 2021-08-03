import requests


class Airtable():

    def __init__(self, apikey, base_id):
        self.base_id = base_id
        self.apikey = apikey
        self.baseurl = 'https://api.airtable.com/v0'

    def _get_url(self, tabname):
        return f'{self.baseurl}/{self.base_id}/{tabname}'

    def get_table(self, tabname, params=None):
        url = self._get_url(tabname)
        headers = {
            'Authorization': f'Bearer {self.apikey}'
        }

        try:
            print(f'Doing GET to {url}')
            result = requests.get(url, headers=headers, params=params)
            return result.json()
        except OSError as err:
            print("ERROR!", err)

    def patch_table(self, tabname, payload):
        url = self._get_url(tabname)
        headers = {
            'Authorization': f'Bearer {self.apikey}',
            'Content-Type': 'application/json'
        }

        try:
            result = requests.patch(url, headers=headers, json=payload)
            # print(result.text)
            print("Request succesful")
        except OSError as err:
            print("ERROR!", err)
