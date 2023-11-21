# Diary to latex
> It converts .txt diary files in a particular folder structure into a latex document

I have diary entries organised in folders of the form

diary_A/\
diary_B/\
diary_C/\
...

This script creates a latex file in the latex book class, with chapters
A\
B\
C\
Within each chapter, the different entries come as different sections. The entries are sorted alphabetically, so it's useful if the entries are of the form YYYY_MM_DD.

## Installation

No installation required. Just run the script.

## Usage example

```
python diary_to_latex.py diary/diary_*/*.txt diary.tex
```

