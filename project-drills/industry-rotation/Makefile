.PHONY: run test clean

run:
	python3 scripts/run_backtest.py

test:
	python3 -m unittest discover tests

clean:
	rm -f data/processed/*.csv outputs/*.csv outputs/figures/*.png
