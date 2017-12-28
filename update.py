#!/usr/bin/env python

import argparse
import os
import subprocess

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('branch')
    parser.add_argument('--commit', action='store_true')
    parser.add_argument('--push', action='store_true')
    return parser.parse_args()

def cd_to_project_root():
    os.chdir(os.path.dirname(__file__))

def copy_files(branch):
    subprocess.check_call(['git', 'checkout', branch, 'apps'])
    subprocess.check_call(['git', 'checkout', branch, 'utils'])
    subprocess.check_call(['git', 'checkout', branch, 'docs'])
    subprocess.check_call(['git', 'add', 'apps', 'docs'])

def has_changes():
    rv = subprocess.call(['git', 'diff-index', '--quiet', 'HEAD', '--'])
    return rv != 0

def commit_changes():
    subprocess.check_call([
        'git', 'commit',
        '--author', 'DeployBot <admin+pcf-deploy-bot@pculture.org>',
        '-m', 'Updating docs',
    ])

def push_changes():
    subprocess.check_call(['git', 'push'])

def main():
    args = parse_args()
    cd_to_project_root()
    copy_files(args.branch)
    if has_changes():
        if args.commit or args.push:
            commit_changes()
        if args.push:
            push_changes()

if __name__ == '__main__':
    main()
