default:
	just --list

eq-viz-small:
	python -m scripts.eq_viewer data_exploration/small
	
eq-viz-big:
	python -m scripts.eq_viewer data_exploration/big
