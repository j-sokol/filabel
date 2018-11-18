import sys
import requests
import json
import re
import fnmatch

from .config import config, config_labels_parsed, github_url, github_api_url, color



class GitHub():
    """docstring for GitHub"""
    def __init__(self, token, session=None):
        self.token = token
        self.session = session or requests.Session()
        self.session.headers = {'User-Agent': 'filabel'}
        self.session.auth = self.add_token

        # self.head = {'Authorization': 'token {}'.format(token)}

    def add_token(self, req):
        """
        This alters all our outgoing requests
        """
        req.headers['Authorization'] = 'token ' + self.token
        return req

    def paginated_get(self, url):
        response = self.session.get(url)
        if response.status_code != 200:
            raise Exception('Fetching url {} failed.'.format(url))

        json_payload = json.loads(response.text)

        while 'next' in response.links.keys():
            response = self.session.get(response.links['next']['url'])
            json_payload.extend(response.json())
            if response.status_code != 200:
                raise Exception('Fetching url {} failed.'.format(url))

        return json_payload
    

    def get_issue(self, slug, pull_request_number):
        url = "{0}/repos/{1}/issues/{2}".format(github_api_url, slug, pull_request_number)
        return self.paginated_get(url)


    def get_pr_files(self, slug, pull_request_number):
        url = "{0}/repos/{1}/pulls/{2}/files?per_page=100&page=1".format(github_api_url, slug, pull_request_number)
        return self.paginated_get(url)


    def get_all_prs(self, slug, state='open', base=False):
        if base:
            with_base = "&base=" + base
        else:
            with_base = ""
        url = "{0}/repos/{1}/pulls?state={2}&per_page=100&page=1{3}".format(github_api_url, slug, state, with_base)
        return self.paginated_get(url)


    def delete_label(self, slug, pull_request_number, label):
        response = self.session.delete("{0}/repos/{1}/issues/{2}/labels/{3}".format(github_api_url, slug, pull_request_number, label))
        if response.status_code != 200:
            raise Exception('DELETing label failed.')
        return 0


    def post_label(self, slug, pull_request_number, label):
        response = self.session.post("{0}/repos/{1}/issues/{2}/labels".format(github_api_url, slug, pull_request_number, label), json=[label])
        # print( response.status_code, response.text)
        if response.status_code != 200:
            raise Exception('POSTing label failed.')
        return 0

    def get_user(self):
        url = "{0}/user".format(github_api_url)
        return self.paginated_get(url)


    def assign_labels_to_changed_files(self, files):
        labels = set()
        for label in config_labels_parsed:
            for pattern in config_labels_parsed[label]:
                # print (label, pattern, files_changed)
                regex = re.compile(fnmatch.translate(pattern))
                files_matching = list(filter(regex.match, files))
                if files_matching:
                    labels.add(label)

        return labels

    def report_log(self, log):
        for label in sorted(log, key=lambda x: x[1]):
            # print("    {} {}".format(label[0], label[1]))
            if label[0] == '+':
                print("    {0}+ {1}{2}".format(color.GREEN, label[1], color.END))
            if label[0] == '-':
                print("    {0}- {1}{2}".format(color.RED, label[1], color.END))
            if label[0] == '=':
                print("    = {}".format(label[1]))


    def label_pr(self, slug, pull_request, delete_old=True):
        """
        Labels pull request by info provided in configuration.
        """

        # Fetch files from PR
        response_files_changed = self.get_pr_files(slug, pull_request['number'])

        # Fetch associated issue for labels
        pr_issue = self.get_issue(slug, pull_request['number'])


        old_labels = { label['name'] for label in pr_issue['labels']}
        files_changed = [ file['filename'] for file in response_files_changed]

        # Check if labels from config match to any files
        new_labels = self.assign_labels_to_changed_files(files_changed)


        new_labels_all = set(config_labels_parsed.keys())
        new_labels_not_added = new_labels_all - new_labels

        labels_log = []
      
        # POST new labels and print it
        for label in new_labels - old_labels:
            self.post_label(slug, pull_request['number'], label)
            labels_log.append(('+', label))


        if delete_old:
            # Remove labels that are not added in this run
            for label in new_labels_not_added.intersection(old_labels):
                self.delete_label(slug, pull_request['number'], label)

                labels_log.append(('-', label))

            for label in new_labels.intersection(old_labels):
                labels_log.append(('=', label))

        # Print out changed labels to stdout
        print("{0}  PR{1} {2}/{3}/pull/{4} - {5}{6}OK{7}".format(color.BOLD, color.END, github_url, slug, pull_request['number'], color.GREEN,color.BOLD,color.END))
        self.report_log(labels_log)

    def get_prs(self, reposlugs, state='open', base=None, delete_old=True):
        """
        Gets all pullrequests for provided repo.
        """

        for slug in reposlugs:
            # Test if reposlug has specified format
            if slug.count("/") != 1:
                print("Reposlug", slug, "not valid!", file=sys.stderr)
                sys.exit(1)

        for slug in reposlugs:
            pull_requests = []
            try:
                pull_requests =  self.get_all_prs(slug, state, base)
                print("{0}REPO{1} {2} - {3}{4}OK{5}".format(color.BOLD, color.END, slug, color.GREEN,color.BOLD,color.END))

            except Exception as e:
                print("{0}REPO{1} {2} - {3}{4}FAIL{5}".format(color.BOLD, color.END, slug, color.RED,color.BOLD,color.END))

            for pull_request in pull_requests:
                self.label_pr(slug, pull_request, delete_old)

                # try:
                #     self.label_prs(pull_request, slug, delete_old)
                # except:
                #     print("{0}  PR{1} {2}/{3}/pull/{4} - {5}{6}FAIL{7}".format(color.BOLD, color.END, github_url, slug, pull_request['number'], color.RED,color.BOLD,color.END))
                #     continue
