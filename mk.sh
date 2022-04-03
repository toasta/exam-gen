#! /bin/bash

_venv/bin/python mk.py > a.tex && \
    pdflatex a.tex && \
    pdflatex a.tex
