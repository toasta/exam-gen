#! /bin/bash

_venv/bin/python mk2.py && \
    pdflatex a.tex && \
    pdflatex a.tex && \
    pdflatex a.tex
