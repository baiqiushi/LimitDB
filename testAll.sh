#!/usr/bin/env bash
python -u TestSubset.py |& tee -a testSubset.log
python -u TimeOverK_Without_vs_WithOrderBy.py |& tee -a timeOverK.log
python -u LimitModeler.py |& tee -a limitModeler.log