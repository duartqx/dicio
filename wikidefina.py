#!/usr/bin/env python

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
        return f'\n\033[1;32m{self.word.title()}\n\n\033[00m{self.descr}\n'

    def _normalize_word(self) -> str:
        ''' returns the word without accents, cedilha, etc
         to be concatenated with the api_url and used to get a response '''
        return ''.join([c for c in nrmlze('NFKD', self.word) if not comb(c)])

    def _get_response(self) -> dict[str, str]:
        try:
            response = urlopen(self.api_url + self.nrmlized)
            return json.load(response)
        except HTTPError:
            return {'source': 'Result not Found'}

    def _get_description(self) -> str:

        ''' Cleans up self.response['source'] with re.sub using to_sub
        dictionary, removes some unneeded text from the start and end of the
        string by spliting it on \n\n and returns the string '''
        descr: str = self.response['source']

        for method in [self._splitter, self._sub]:
            descr = method(descr)

        return descr.strip()

    @staticmethod
    def _splitter(s: str) -> str:
        splitter: list[str] = [
            'Tradução', 'Expressões', 
            'etimologia', 'Sinônimos', 'pronúncia'
        ]
        for term in splitter:
            # Removes irrelevant information
            if term in s:
                s = ''.join(s.split(term)[0])
        return s

    @staticmethod
    def _sub(s: str) -> str:

        sub_patterns: list[str] = [ 
            '\|',
            r'\*.*|Notas.*|\-pt\-|\<(.*?)\>|wiki(.*?)\:|',
            r'({{Wiki|Imagem|ver também)(.*?)\n',
            '=+|  |\{\{\}\}|\{\{$',
            '\n\n+',
            r'(?:#)(.*)',
            '\[\[',
            '\{\{',
            '\]\]|\}\}',
            r'(?:==+)(.*?)(?:==+)',
            '\x1b\[1m\x1b\[3m\n\n',
            '⚫\n\n',
        ]

        sub_repl: list[str] = [
            ' | ', '', '', '', '\n\n', r'⚫\1', 
            '\033[1m', '\033[3m', '\033[00m', 
            r'\033[3m\1\033[00m\n', '', '\n',
        ]

        for pattern, repl in zip(sub_patterns, sub_repl):
            # for loop on a zip of two lists to make sure they are looping on
            # the right order
            s = sub(pattern, repl, s)

        return s


def main() -> None:
    try: word: str = argv[1]
    except IndexError: print('\nNo search word provided\n'); return
    print(DicioDefinition(word))

if __name__ == '__main__':

    main()
