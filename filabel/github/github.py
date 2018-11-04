import sys
import requests
import json
import re
import fnmatch

from ..config.config import config, config_labels_parsed, github_url, github_api_url, color

def label_prs(pull_request, slug, head, delete_old=True):
    """
    Labels pull requests by info provided in configuration.
    """

    # Fetch files from PR
    response = requests.get("{0}/repos/{1}/pulls/{2}/files?per_page=100&page=1".format(github_api_url, slug, pull_request['number']), headers=head)
    if response.status_code != 200:
        raise Exception('Fetching PR failed.')


    response_files_changed = json.loads(response.text)

    while 'next' in response.links.keys():
        response = requests.get(response.links['next']['url'], headers=head)
        response_files_changed.extend(response.json())
        if response.status_code != 200:
            print("{0}REPO{1} {2} - {3}{4}FAIL{5}".format(color.BOLD, color.END, slug, color.RED,color.BOLD,color.END))
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


def get_prs(reposlugs, state='open', base=None, delete_old=True):
    """
    Gets all pullrequests for provided repo.
    """

    head = {'Authorization': 'token {}'.format(config['github']['token'])}
    for slug in reposlugs:

        # Test if reposlug has specified format
        if slug.count("/") != 1:
            print("Reposlug", slug, "not valid!", file=sys.stderr)
            sys.exit(1)

    for slug in reposlugs:

        # Fetch all PRs
        if base:
            with_base = "&base=" + base
        else:
            with_base = ""

        response = requests.get("{0}/repos/{1}/pulls?state={2}&per_page=100&page=1{3}".format(github_api_url, slug, state, with_base), headers=head)

        if response.status_code != 200:
            print("{0}REPO{1} {2} - {3}{4}FAIL{5}".format(color.BOLD, color.END, slug, color.RED,color.BOLD,color.END))
            continue

        pull_requests = json.loads(response.text)


        while 'next' in response.links.keys():
            response = requests.get(response.links['next']['url'], headers=head)
            pull_requests.extend(response.json())
            if response.status_code != 200:
                print("{0}REPO{1} {2} - {3}{4}FAIL{5}".format(color.BOLD, color.END, slug, color.RED,color.BOLD,color.END))
                continue


        print ("{0}REPO{1} {2} - {3}{4}OK{5}".format(color.BOLD, color.END, slug, color.GREEN,color.BOLD,color.END))

        for pull_request in pull_requests:
            try:
                label_prs(pull_request, slug, head, delete_old)
            # except Exception as e: 
            #     print(e)
            except:
                print("{0}  PR{1} {2}/{3}/pull/{4} - {5}{6}FAIL{7}".format(color.BOLD, color.END, github_url, slug, pull_request['number'], color.RED,color.BOLD,color.END))
                # sys.exit(1)
                continue
