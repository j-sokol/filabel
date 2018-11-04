# filabel


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

##  How to deploy to Heroku (web based)

```
clone the repo
heroku create
git push heroku web
heroku config:set FILABEL_CONFIG=./test/fixtures/labels.abc.cfg
heroku config:set GH_TOKEN=---your token---
heroku config:set GH_USER=---your username---
heroku config:set GH_SECRET=---your github secret---
```

