#!/usr/bin/env python

from urllib.request import urlopen
from urllib.error import HTTPError
from unicodedata import normalize, combining
from re import search, sub
from sys import argv
from typing import Optional, Match

class NotFoundError(Exception): pass

class Description:
    
    def __init__(self, word):
        self.word = word
        self.nrml_word = self.normalize_word()
        self.description = self.get_description()

    def __repr__(self):
        ''' Returns word capitalized + the description (that can be 'Result 
        not found') 
        The weird encoded characters around the word are an ANSI escape
        sequence that causes the word to be printed in the color green in the
        terminal, instead of the default white '''
        return f"\n\033[1;32m{self.word.capitalize()}\033[00m\n\n    " + \
               f"{self.description}\n"

    def normalize_word(self) -> str:
        ''' normalize_word returns the word without accents, cedilha, etc
         to be concatenated with the URL_BASE and used to get a response '''
        return ''.join([c for c in normalize('NFKD',self.word)
            if not combining(c)])

    def _get_result(self) -> str:
        ''' Returns the html content of dicio.com.br + self.norm_word or raises
        NotFoundError exception if the word was not found '''
        URL_BASE: str = 'https://www.dicio.com.br/'
        try:
            content: str = urlopen(URL_BASE + self.nrml_word).read().decode()
        except HTTPError:
            raise NotFoundError
        
        result: Optional[Match[str]] = search('<p itemprop="description" ' + \
                                       'class=*(.*)</p>', content)
        
        # This one was to make mypy happy about None not having group()
        if result:
            return result.group()
        else:
            raise NotFoundError

    def get_description(self) -> str:
        try:
            result: str = self._get_result()
            if 'Ainda não temos o significado' in result:
                # if the word is not on dicio.com.br, result can be None, if
                # it's gibberish, or it can be a warning that the word is not
                # on the site if it's a word with similar results on the site
                # Raising error to avoid returning two types (NoneType or Str)
                raise NotFoundError
        except NotFoundError:
            return 'Result not found'
        
        t = '. '.join(sub('<.*?>','',result).split('.'))
        # to format the description first re.sub is used here to  removes 
        # all html tags like <span> </span> <p> that it can find. 
        # That can lead to some words being united with a dot were a tag 
        # was before, so the split('.') removes all dots and the string is
        # joined again with '. '.join()
        # Finally split is used again on ';' to separate the description 
        # in multiple lines like it is presented on dicio.com.br's page
        description = ';\n    '.join(l.capitalize() for l in t.split('; '))
        return description


if __name__ == '__main__':

    # Talvez seja interessante eu alterar a fonte de descrição para a API do
    # wikitionário em vez de usar regex em uma página do dicio.
    # https://pt.wiktionary.org/w/rest.php/v1/page/<word>
    word: str = argv[1]
    print(Description(word))
