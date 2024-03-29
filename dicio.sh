#!/usr/bin/env bash

word="$2"

UND=$(tput smul)
NOUND=$(tput rmul)
BLD=$(tput bold)
NRML=$(tput sgr0)

usageHelp() {
    cat <<_EOF
${BLD}NAME${NRML}
   dicio - A simple script that checks spelling
with GNU Aspell or defines a word with the help
of online dicionaries

${BLD}USAGE:${NRML}
   dicio [OPTION] ${UND}<word>${NOUND}   

${BLD}OPTIONS:${NRML}                          
   pt           checks spelling of pt_BR word
   us|en        checks spelling of en_US word
   d            prints portuguese word definition
   t en         translates words from english to portuguese
   t pt         translates words from portuguese to english
_EOF
}

aspell_checker() {
    # depends on:
    # GNU aspell
    # aspell-pt for the pt_BR and pt_PT languages
    # aspell-en for the en_US language
    # -l option chooses the languages
    # -a option gets the word via stdin, incoming from echo
    # sed removes the first 2 lines
    echo "$word" | aspell -l "$1" -a | sed -n 2p
}

[[ -z $word ]] && usageHelp && exit 1
# If no word is passed as the second argument it echoes the help message

case "$1" in
pt)
    aspell_checker pt_BR
    ;;
us | en)
    aspell_checker en_US
    ;;
d)
    # External python script that get pt_BR word description
    defina-pt "$word"
    ;;
t)
    shift
    case "$1" in
    en)
        trans -s en -t pt "$2" -b
        ;;
    pt)
        trans -s pt -t en "$2" -b
        ;;
    esac
    ;;
*)
    usageHelp
    ;;
esac
