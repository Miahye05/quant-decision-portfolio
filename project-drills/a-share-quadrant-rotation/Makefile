.PHONY: sample figures test clean

sample:
	python3 scripts/run_quadrant_rotation.py --data-source sample

figures:
	python3 scripts/generate_readme_figures.py --target-quadrant low_low

test:
	python3 -m unittest discover tests

clean:
	rm -f data/processed/*.csv outputs/*.csv outputs/*.xlsx outputs/figures/*.png
