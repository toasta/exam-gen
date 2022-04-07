#! /bin/bash

_venv/bin/python mk2.py > a.tex && \
    pdflatex a.tex && \
    pdflatex a.tex && \
    pdflatex a.tex
