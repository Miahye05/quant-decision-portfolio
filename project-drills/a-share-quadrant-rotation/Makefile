.PHONY: sample test clean

sample:
	python3 scripts/run_quadrant_rotation.py --data-source sample

test:
	python3 -m unittest discover tests

clean:
	rm -f data/processed/*.csv outputs/*.csv outputs/*.xlsx outputs/figures/*.png
