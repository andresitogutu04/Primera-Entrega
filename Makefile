# simple makefile to simplify repetetive build env management tasks under posix

PYTHON ?= python
CTAGS ?= ctags

all: clean inplace test

clean-pyc:
	find . -name "*.pyc" | xargs rm -f

clean-so:
	find . -name "*.so" | xargs rm -f
	find . -name "*.pyd" | xargs rm -f

clean-build:
	rm -rf build

clean-ctags:
	rm -f tags

clean: clean-build clean-pyc clean-so clean-ctags

in: inplace # just a shortcut
inplace:
	$(PYTHON) setup.py build_ext -i

nosetests: nose # alias

# Test conditions

nose: clean
	python make test nose

nose_coverage: clean
	python make test nose 1

test: clean
	python make test full

flake: clean
	python make test flake

flake3: clean
	python3 make test flake

lineendings: clean
	python make test lineendings

extra: clean
	python make test extra

nobackend : clean
	python make test nobackend

pyqt4: clean
	python make test pyqt4

pyside: clean
	python make test pyside

pyglet: clean
	python make test pyglet

glfw: clean
	python make test glfw

sdl2: clean
	python make test sdl2

glut: clean
	python make test glut

ipynb_vnc: clean
	python make test ipynb_vnc
