default:
	just --list

eq-viz-small:
	python -m scripts.eq_viewer event data/small
	
eq-viz-big:
	python -m scripts.eq_viewer event data/big

eq-viz-multi:
	python -m scripts.eq_viewer multi-event data/

eq-viz-station-WKYH03:
	python -m scripts.eq_viewer station data/small/kik/WKYH032404210619

prep-extract-root:
	python -m scripts.prep.eq_extract ./ ./data
