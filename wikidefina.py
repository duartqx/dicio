#!/usr/bin/env python

from json import load
from re import sub, split
from sys import argv
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen, urljoin

class NotFoundError(HTTPError): pass

class DicioDefinition:

    def __init__(self, word: str) -> None:
        self.word: str = word.lower()
        self.api_url: str = 'https://pt.wiktionary.org/w/rest.php/v1/page/'
        self.response: dict[str, str] = self._get_response()
        self.descr: str = self._get_description()

    def __repr__(self) -> str:
        return f'\n\033[1;32m{self.word.title()}\n\n\033[00m{self.descr}\n'

    def _get_response(self) -> dict[str, str]:
        ''' Returns a dictionary, received by calling urlopen with self.api_url
        + self.nrmlized, that contains the raw description in the 'source'
        key.'''
        try:
            response = urlopen(self.api_url + quote(self.word))
            return load(response)
        except HTTPError:
            return {'source': 'Result not Found'}

    def _get_description(self) -> str:
        ''' Cleans up self.response['source'] by removing some unneeded text by
        splitting the string in some terms with self._splitter and making
        substitutions with self._sub '''
        descr: str = self.response['source']

        for method in [self._splitter, self._sub]:
            descr = method(descr)

        #print(repr(descr.strip()))
        return descr.strip()

    @staticmethod
    def _splitter(s: str) -> str:
        ''' Splits s with re.split on all lines starting with a # and returns
        everything other than the last item on the split to remove unneeded
        informations '''
        return ''.join(split(r'((?:#))(.*)', s)[:-1])

    @staticmethod
    def _sub(s: str) -> str:
        ''' zips patterns and replacements and calls sub with then to clean up
        s '''
        patterns: list[str] = [ 
            '\|',
            r'\*.*|Notas.*|\-pt\-|\<(.*?)\>|wiki(.*?)\:|',
            r'({{Wiki|Imagem|ver também)(.*?)\n',
            '=+|  |\{\{\}\}|\{\{$',
            '\n\n+',
            r'(?:#)(.*)',
            '\[\[|\:\'\'\'',
            '\{\{',
            '\]\]|\}\}|\'\'\'',
            r'(?:==+)(.*?)(?:==+)',
            '\x1b\[1m\x1b\[3m\n\n',
            '⚫($|\n+)', '\'\'',
            '\x1b\[1m(\n+)|\x1b\[3m(\n+)|(\n+)\x1b\[1m', 
        ]
        replacements: list[str] = [
            ' | ', '', '', '', '\n\n', r'⚫\1', 
            '\033[1m', '\033[3m', '\033[00m', 
            r'\033[3m\1\033[00m\n', '', '\n', '\"', '',
        ]

        for pattern, repl in zip(patterns, replacements):
            # for loop on a zip of two lists to make sure they are looping on
            # the right order
            s = sub(pattern, repl, s)

        return s

def main() -> None:
    ''' Calls the DicioDefinition class if a word is passed as argv[1] '''
    try: word: str = argv[1]
    except IndexError: print('\nNo search word provided\n'); return
    print(DicioDefinition(word))

if __name__ == '__main__':

    main()
