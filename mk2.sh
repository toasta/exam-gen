#! /bin/bash

PDFL="pdflatex -output-directory out/"

_venv/bin/python mk2.py && \
    $PDFL a.tex && \
    $PDFL a.tex && \
    $PDFL a.tex && \
    $PDFL a.tex && \
    $PDFL a.tex && \
    $PDFL a.tex
