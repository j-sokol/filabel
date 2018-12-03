import click
import requests
import fnmatch
import json
import re
import sys
from pprint import pprint

import os

from .github import GitHub
from .config import config, config_labels_parsed, session

github_api_url = 'https://api.github.com'
github_url = 'https://github.com'

def parse_config(config_auth, config_labels):
    """
    Load configuration from provided files.
    """
    if config_auth == None:
        print ("Auth configuration not supplied!", file=sys.stderr)
        sys.exit(1)
    # Parse auth config
    try:
        config.read_string(config_auth.read())
        if config['github']['token'] == None:
            raise Exception('Token variable not provided.')
    except:
        print ("Auth configuration not usable!", file=sys.stderr)
        sys.exit(1)

    if config_labels == None:
        print ("Labels configuration not supplied!", file=sys.stderr)
        sys.exit(1)
    # Parse label config
    try:
        config.read_string(config_labels.read())

        if config['labels'] == None:
            raise Exception('Labels variables not provided.')

        # Parse labels from string to readable format
        for config_key in config['labels']:
            config_labels_parsed[config_key] = list(filter(None,config['labels'][config_key].splitlines()))
    except:
        print ("Labels configuration not usable!", file=sys.stderr)
        sys.exit(1)


@click.command()
@click.pass_obj
@click.option('-s', '--state', default="open", help='Filter pulls by state.  [default: open]',  type=click.Choice(['open', 'closed', 'all']))
@click.option('-d/-D', '--delete-old/--no-delete-old', default="true", help='Delete labels that do not match anymore.   [default: True]')
@click.option('-b', '--base', metavar='BRANCH', help='Filter pulls by base (PR target) branch name.')
@click.option('-a', '--config-auth', metavar='FILENAME', help='File with authorization configuration.', type=click.File('r'))
@click.option('-l', '--config-labels',  metavar='FILENAME',help='File with labels configuration.', type=click.File('r'))

@click.argument('reposlugs', nargs=-1)



def cli(obj, state, config_auth, base, delete_old, config_labels, reposlugs):
    """
    CLI tool for filename-pattern-based labeling of GitHub PRs.
    """
    config_labels_parsed = parse_config(config_auth, config_labels)

    if obj and obj['session']:
        github = GitHub(config['github']['token'], obj['session'])
    else:
        github = GitHub(config['github']['token'])


    github.get_prs(reposlugs, state, base, delete_old)
