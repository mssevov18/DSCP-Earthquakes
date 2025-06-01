default:
	just --list

eq-viz-small:
	python -m scripts.eq_viewer data/small
	
eq-viz-big:
	python -m scripts.eq_viewer data/big
