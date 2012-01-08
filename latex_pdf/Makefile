T=<filename>
FIGS = figures/<file>.svg

SRC = $T.tex abs.tex intro.tex remote.tex design.tex eval.tex conc.tex \
	$(FIGS:.svg=.pdf)

.SUFFIXES: .eps .fig .pdf .svg

.svg.pdf:
	inkscape $< --export-pdf=$@
.fig.eps:
	fig2dev -L eps -p 0 $< $@
.fig.pdf:
	fig2dev -L pdf -p 0 $< $@

$T.pdf: $(SRC)
	pdflatex $T
	make $T.bbl
	pdflatex $T
	pdflatex $T


$T.ps: $(SRC) $T.bbl $(FIGS:.fig=.eps)
	latex $T

$T.aux:
	@echo "***************************"
	@echo "Making .aux file for bibtex"
	@echo "***************************"
	pdflatex $T

$T.bbl: $T.aux latex8.bst
	@echo "*************************"
	@echo "Making .bbl file (bibtex)"
	@echo "*************************"
	-bibtex $T

clean:
	rm -f $T.log $T.aux $T.out $T.toc $T.bbl $T.blg
	rm -f $(FIGS:.svg=.pdf)
	rm -f *~ 
	rm -f $T.pdf

figures:
	fig2dev -L pdf -p 0 $< $@
