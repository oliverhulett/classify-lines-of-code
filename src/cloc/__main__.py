#!/usr/bin/python2.7
# encoding: utf-8
'''
cloc.__main__ -- shortdesc

cloc.__main__ is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2018 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
import argparse
import logging
import glob
import re
import yaml

from cloc.classification_description import ClassificationDescription
from cloc.line_classifier import LineClassifier
from cloc.line_collection import LineCollection
from cloc.text_reporter import TextReporter


__version__ = 0.1
__updated__ = '2018-03-03'


def main(argv=None):
    '''Main method.  Handle command line arguments.'''
    
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    
    # Setup argument parser
    parser = argparse.ArgumentParser(
        'classify_lines_of_code',
        description='''
            Classify lines of code is a configuration driven LOC counter.  It matches lines of code based on regular
            expressions found in the configuration file(s).  The configuration file(s) allow nested sections so that
            the set of regular expressions used to match lines can change based on a filename pattern and/or a
            previous match.
        ''',)
    parser.add_argument("-l", "--logconfig", metavar="path",
                        help="use logging configuration file [default: %(default)s]")
    parser.add_argument("-c", "--config", metavar="path", nargs="+",
                        help="use configuration file [default: %(default)s]")
    parser.add_argument("-i", "--include", metavar="RE",
                        help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]")
    parser.add_argument("-e", "--exclude", metavar="RE",
                        help="exclude paths matching this regex pattern. [default: %(default)s]")
    parser.add_argument('-V', '--version', action='version', version=program_version_message)
    parser.add_argument(dest="paths", metavar="path", nargs='+',
                        help="paths to folder(s) with source file(s) [default: %(default)s]")
    
    # Process arguments
    args = parser.parse_args()
    
    _setup_logging(args.logconf)
    
    if args.include and args.exclude and args.include == args.exclude:
        raise Exception("include and exclude pattern are equal! Nothing will be processed.")
    include_pattern = re.compile(args.include) if args.include else None
    exclude_pattern = re.compile(args.exclude) if args.exclude else None 
    
    classification_description = ClassificationDescription()
    _etc = os.path.join('/', 'etc', 'cloc')
    _home = os.path.expanduser(os.path.join('~', '.cloc'))
    _default_files = (os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cloc.yml'),)
    _default_files += sorted(glob.glob(os.path.join(_etc, '*.yml')) + glob.glob(os.path.join(_etc, '*.yaml')) + glob.glob(os.path.join(_etc, '*.json')))
    _default_files += sorted(glob.glob(os.path.join(_home, '*.yml')) + glob.glob(os.path.join(_home, '*.yaml')) + glob.glob(os.path.join(_home, '*.json')))
    for config_file in _default_files:
        if os.path.exists(config_file):
            classification_description.add_descriptions(yaml.load(open(config_file, 'r').read()))
    
    for config_file in args.config:
        classification_description.add_descriptions(yaml.load(open(config_file, 'r').read()))
    
    _log_startup(args, classification_description)
    
    line_collection = LineCollection()
    classifier = LineClassifier(classification_description, line_collection)
    
    for path in args.paths:
        for dirpath, _, fnames in os.walk(path):
            if not _should_process_file(include_pattern, exclude_pattern, dirpath):
                line_collection.skipped_directory(dirpath)
                continue
            for f in fnames:
                if not _should_process_file(include_pattern, exclude_pattern, f):
                    line_collection.skipped_file(f)
                    continue
                classifier.classify_file(f)
    
    reporter = TextReporter(line_collection)
    reporter.report()
    return 0

def _setup_logging(logconf):
    pass

def _log_startup(args, classification_description):
    pass

def _should_process_file(include_pattern, exclude_pattern, f):
    if include_pattern and not include_pattern.matches(f):
        logging.info("Skipping file not matched by include pattern: %s", f)
        return False
    if exclude_pattern and exclude_pattern.matches(f):
        logging.info("Skipping file matched by exclude pattern: %s", f)
        return False
    return True

if __name__ == "__main__":
    sys.exit(main())