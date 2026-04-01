# Makefile for ICAPS 2026 demo paper
#
# Usage:
#   make        — full build (pdflatex → bibtex → pdflatex × 2)
#   make quick  — single pdflatex pass (for draft previews)
#   make clean  — remove all generated files except main.pdf
#   make purge  — remove all generated files including main.pdf

MAIN    = main
LATEX   = pdflatex
BIBTEX  = bibtex
FLAGS   = -interaction=nonstopmode -halt-on-error

.PHONY: all quick clean purge

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib
	$(LATEX) $(FLAGS) $(MAIN)
	$(BIBTEX) $(MAIN)
	$(LATEX) $(FLAGS) $(MAIN)
	$(LATEX) $(FLAGS) $(MAIN)

quick:
	$(LATEX) $(FLAGS) $(MAIN)

clean:
	rm -f $(MAIN).aux \
	      $(MAIN).bbl \
	      $(MAIN).blg \
	      $(MAIN).log \
	      $(MAIN).out \
	      $(MAIN).toc \
	      $(MAIN).lof \
	      $(MAIN).lot \
	      $(MAIN).fls \
	      $(MAIN).fdb_latexmk \
	      $(MAIN).synctex.gz \
	      texput.log

purge: clean
	rm -f $(MAIN).pdf
