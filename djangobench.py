#!/usr/bin/env python

"""
Run us some Django benchmarks.
"""

import os
import subprocess
import tempfile

import argparse
from unipath import DIRS, FSPath as Path

import perf

BENCMARK_DIR = Path(__file__).parent.child('benchmarks')

def main(control, experiment, benchmark_dir=BENCMARK_DIR):
    # Calculate the subshell envs that we'll use to execute the
    # benchmarks in.
    control_env = {
        'PYTHONPATH': "%s:%s" % (Path(benchmark_dir).absolute(), Path(control).parent.absolute()),
    }
    experiment_env = {
        'PYTHONPATH': "%s:%s" % (Path(benchmark_dir).absolute(), Path(experiment).parent.absolute()),
    }
    
    # TODO: make this configurable, or, better, make it an option
    # to run until results are significant or some ceiling is hit.
    trials = 5
    
    results = []

    for benchmark in discover_benchmarks(benchmark_dir):
        print "Running '%s' benchmark ..." % benchmark.name
        settings_mod = '%s.settings' % benchmark.name
        control_env['DJANGO_SETTINGS_MODULE'] = settings_mod
        experiment_env['DJANGO_SETTINGS_MODULE'] = settings_mod
        
        control_data = perf.MeasureCommand(
            ['python', '%s/benchmark.py' % benchmark],
            iterations = trials,
            env = control_env,
            track_memory = False,
        )
        
        experiment_data = perf.MeasureCommand(
            ['python', '%s/benchmark.py' % benchmark],
            iterations = trials,
            env = experiment_env,
            track_memory = False,
        )
        
        options = argparse.Namespace(
            track_memory = False, 
            diff_instrumentation = False,
            benchmark_name = benchmark.name,
            disable_timelines = True
        )
        result = perf.CompareBenchmarkData(control_data, experiment_data, options)
        print result
        print
    
def discover_benchmarks(benchmark_dir):
    for app in Path(benchmark_dir).listdir(filter=DIRS):
        if app.child('benchmark.py').exists() and app.child('settings.py').exists():
            yield app

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--control',
        default = 'django-control/django',
        help = "Path to the Django code tree to use as control."
    )
    parser.add_argument(
        '--experiment',
        default = 'django-experiment/django',
        help = "Path to the Django version to use as experiment."
    )
    args = parser.parse_args()
    main(args.control, args.experiment)