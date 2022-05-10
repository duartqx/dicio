from unicodedata import normalize as nrmlze, combining as comb
from urllib.request import urlopen
from urllib.error import HTTPError
from sys import argv
from re import sub
import json

class NotFoundError(HTTPError): pass

class DicioDefinition:

    def __init__(self, word: str) -> None:
        self.word: str = word.lower()
        self.nrmlized: str = self._normalize_word()
        self.api_url: str = 'https://pt.wiktionary.org/w/rest.php/v1/page/'
        self.response: dict[str, str] = self._get_response()
        self.descr: str = self._get_description()

    def __repr__(self) -> str:
        return f'\n\033[32m{self.word.title()}\033[00m\n{self.descr.strip()}\n'

    def _normalize_word(self) -> str:
        ''' normalize_word returns the word without accents, cedilha, etc
         to be concatenated with the URL_BASE and used to get a response '''
        return ''.join([c for c in nrmlze('NFKD', self.word) if not comb(c)])

    def _get_response(self) -> dict[str, str]:
        try:
            response = urlopen(self.api_url + self.nrmlized)
        except HTTPError:
            if response.code == 400:
                return {'source': 'Bad request'}
            elif response.code == 401:
                return {'source': 'Unauthorized request'}
            elif response.code == 403:
                return {'source': 'Forbidden'}
            elif response.code == 404:
                return {'source': 'Not found'}
            elif response.code == 500:
                return {'source': 'Something is wrong with the server'}
        return json.load(response)

    def _get_description(self) -> str:

        to_sub = {'\{\{Wikipédia\}\}\n\n=\{\{\-pt\-\}\}\=\n': '', 
                  '\[\[': '\033[1m', '\]\]|\}\}': '\033[00m', 
                  '\{\{': '\033[3m', 
                  r'(?:==+)(.*?)(?:==+)': r'\033[3m\1\033[00m\n', 
                  '=': ' ',
                  r'(?:#)(.*)': r'⚫\1', 
                  '\-pt\-': '',
                  '\|': ' | ',
                 }
        descr: str = self.response['source']
        if '\n\n' in descr:
            descr = '\n\n'.join(descr.split('\n\n')[1:-2])
        if 'Tradução' in descr:
            descr = ''.join(descr.split('Tradução')[0])

        for key, value in to_sub.items():
            descr = sub(key, value, descr)

        return descr

def main() -> None:
    word: str = argv[1]
    print(DicioDefinition(word))

if __name__ == '__main__':

    main()

