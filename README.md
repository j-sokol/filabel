# filabel

[![Build Status](https://travis-ci.com/j-sokol/filabel.svg?token=BBYqq34pqDpNae8qQbvk&branch=master)](https://travis-ci.com/j-sokol/filabel)

Tool for labeling PRs at GitHub by globs.

## How to run as CLI

```

Usage: filabel.py [OPTIONS] [REPOSLUGS]...

  CLI tool for filename-pattern-based labeling of GitHub PRs

Options:
  -s, --state [open|closed|all]   Filter pulls by state.  [default: open]
  -d, --delete-old / -D, --no-delete-old
                                  Delete labels that do not match anymore.
                                  [default: True]
  -b, --base BRANCH               Filter pulls by base (PR target) branch
                                  name.
  -a, --config-auth FILENAME      File with authorization configuration.
  -l, --config-labels FILENAME    File with labels configuration.
  --help                          Show this message and exit.
```

##  How to deploy to Heroku (web based app)

```
clone the repo
heroku create
git push heroku web
heroku config:set FILABEL_CONFIG=./test/fixtures/labels.abc.cfg
heroku config:set GH_TOKEN=---your token---
heroku config:set GH_USER=---your username---
heroku config:set GH_SECRET=---your github secret---
```

## How to run tests

Just clone the repository, and run:
```
python setup.py test
```
This will run the tests, which are split up into three parts: CLI test, web (flask) tests and unit tests of internal funtions.
In cases when environment variable `GH_TOKEN` is not specified, requests to GitHub API will be replayed from 'cassetes'. For this type of mocking I've used library betamax.

### How to create new betamax cassetes 
If you want to create your own replays of GitHub API requests (so called cassetes), just set `GH_TOKEN` variable. This will override existing jsons in `test/fixtures/cassettes/`.