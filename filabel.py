#!/usr/bin/env python3

import click
import requests
import configparser
import fnmatch
import json
import re
import sys
# from pprint import pprint

# class color:
#    PURPLE = '\033[95m'
#    CYAN = '\033[96m'
#    DARKCYAN = '\033[36m'
#    BLUE = '\033[94m'
#    GREEN = '\033[92m'
#    YELLOW = '\033[93m'
#    RED = '\033[91m'
#    BOLD = '\033[1m'
#    UNDERLINE = '\033[4m'
#    END = '\033[0m'

class color:
   PURPLE = ''
   CYAN = ''
   DARKCYAN = ''
   BLUE = ''
   GREEN = ''
   YELLOW = ''
   RED = ''
   BOLD = ''
   UNDERLINE = ''
   END = ''

github_api_url = 'https://api.github.com'
github_url = 'https://github.com'



@click.command()
@click.option('-s', '--state', default="open", help='Filter pulls by state.  [default: open]',  type=click.Choice(['open', 'closed', 'all']))
@click.option('-d/-D', '--delete-old/--no-delete-old', default="true", help='Delete labels that do not match anymore.   [default: True]')
@click.option('-b', '--base', metavar='BRANCH', help='Filter pulls by base (PR target) branch name.')
@click.option('-a', '--config-auth', metavar='FILENAME', help='File with authorization configuration.', type=click.File('r'))
@click.option('-l', '--config-labels',  metavar='FILENAME',help='File with labels configuration.', type=click.File('r'))

@click.argument('reposlugs', nargs=-1)



def label(state, config_auth, base, delete_old, config_labels, reposlugs):
    """CLI tool for filename-pattern-based labeling of GitHub PRs."""

    config = configparser.ConfigParser()


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
    config_labels_parsed = {}
    try:
        config.read_string(config_labels.read())
        # Parse labels from string to readable format
        for config_key in config['labels']:
            config_labels_parsed[config_key] = list(filter(None,config['labels'][config_key].splitlines()))
    except:
        print ("Labels configuration not usable!", file=sys.stderr)
        sys.exit(1)

    

    head = {'Authorization': 'token {}'.format(config['github']['token'])}
    for slug in reposlugs:

        # Test if reposlug has specified format
        if slug.count("/") != 1:
            print ("Reposlug", slug, "not valid!", file=sys.stderr)
            sys.exit(1)

    for slug in reposlugs:

        # Fetch all PRs
        if base:
            with_base = "&base=" + base
        else:
            with_base = ""

        response = requests.get("{0}/repos/{1}/pulls?state={2}&per_page=100&page=1{3}".format(github_api_url, slug, state, with_base), headers=head)

        if response.status_code != 200:
            print ("{0}REPO{1} {2} - {3}{4}FAIL{5}".format(color.BOLD, color.END, slug, color.RED,color.BOLD,color.END))
            continue

        pull_requests = json.loads(response.text)


        while 'next' in response.links.keys():
            response = requests.get(response.links['next']['url'], headers=head)
            pull_requests.extend(response.json())
            if response.status_code != 200:
                print ("{0}REPO{1} {2} - {3}{4}FAIL{5}".format(color.BOLD, color.END, slug, color.RED,color.BOLD,color.END))
                continue


        print ("{0}REPO{1} {2} - {3}{4}OK{5}".format(color.BOLD, color.END, slug, color.GREEN,color.BOLD,color.END))


        for pull_request in pull_requests:

            try:
                # Fetch files from PR
                response = requests.get("{0}/repos/{1}/pulls/{2}/files?per_page=100&page=1".format(github_api_url, slug, pull_request['number']), headers=head)
                if response.status_code != 200:
                    raise Exception('Fetching PR failed.')


                response_files_changed = json.loads(response.text)

                while 'next' in response.links.keys():
                    response = requests.get(response.links['next']['url'], headers=head)
                    response_files_changed.extend(response.json())
                    if response.status_code != 200:
                        print ("{0}REPO{1} {2} - {3}{4}FAIL{5}".format(color.BOLD, color.END, slug, color.RED,color.BOLD,color.END))
                        continue



                # Fetch associated issue for labels
                response = requests.get("{0}/repos/{1}/issues/{2}".format(github_api_url, slug, pull_request['number']), headers=head)
                if response.status_code != 200:
                    raise Exception('Fetching associated issue failed.')

                pr_issue = json.loads(response.text)

                # Get names of labels already in issue
                old_labels = set()
                for label in pr_issue['labels']:
                    old_labels.add(label['name'])


                files_changed = []
                new_labels = set()

                # Add all changed lists from PR to list
                for file in response_files_changed:
                    files_changed.append(file['filename'])

                # Check if labels from config match to any files
                for label in config_labels_parsed:
                    for pattern in config_labels_parsed[label]:
                        # print (label, pattern, files_changed)
                        regex = re.compile (fnmatch.translate (pattern))
                        files_matching = list(filter(regex.match, files_changed))
                        if files_matching:
                            new_labels.add(label)


                new_labels_all = set(config_labels_parsed.keys())
                new_labels_not_added = new_labels_all - new_labels

                labels_log = []
              

                # POST new labels and print it
                for label in new_labels - old_labels:
                    response = requests.post("{0}/repos/{1}/issues/{2}/labels".format(github_api_url, slug, pull_request['number'], label), json=[label], headers=head)
                    # print (response.text, response.status_code)
                    if response.status_code != 200:
                        raise Exception('POSTing label failed.')
                    labels_log.append(('+', label))


                if delete_old:
                    # Remove labels that are not added in this run
                    for label in new_labels_not_added.intersection(old_labels):
                        response = requests.delete("{0}/repos/{1}/issues/{2}/labels/{3}".format(github_api_url, slug, pull_request['number'], label), headers=head)
                        if response.status_code != 200:
                            raise Exception('DELETing label failed.')

                        labels_log.append(('-', label))

                    for label in new_labels.intersection(old_labels):
                        labels_log.append(('=', label))

                # Print out changed labels to stdout
                print("{0}  PR{1} {2}/{3}/pull/{4} - {5}{6}OK{7}".format(color.BOLD, color.END, github_url, slug, pull_request['number'], color.GREEN,color.BOLD,color.END))          
                for label in sorted(labels_log, key=lambda x: x[1]):
                    # print("    {} {}".format(label[0], label[1]))
                    if label[0] == '+':
                        print("    {0}+ {1}{2}".format(color.GREEN, label[1], color.END))
                    if label[0] == '-':
                        print("    {0}- {1}{2}".format(color.RED, label[1], color.END))
                    if label[0] == '=':
                        print("    = {}".format(label[1]))

            except:
                print ("{0}  PR{1} {2}/{3}/pull/{4} - {5}{6}FAIL{7}".format(color.BOLD, color.END, github_url, slug, pull_request['number'], color.RED,color.BOLD,color.END))
                # sys.exit(1)
                continue

            # print(labels_log)

    



if __name__ == '__main__':
    label()