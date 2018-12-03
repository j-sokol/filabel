#!/bin/bash -eux

# this var is used by hub, it will use the same token = same user
export GITHUB_TOKEN=${GH_TOKEN}



mkdir mi-pyt-test-repo
cd mi-pyt-test-repo
git init
git commit --allow-empty -m'Initial commit'
hub create
git push -u origin master

git checkout -b pr1
touch aaaa bbbb cccc dddd
git add .
git commit -m'Add some files'
git push -u origin pr1
hub pull-request -m'Add some files01'

git checkout master
git checkout -b pr2
touch file{1..222}
git add .
git commit -m'Add many files'
git push -u origin pr2
hub pull-request -m'Add many files02'

git checkout master
git checkout -b pr3
touch file{1..222}
git add .
git commit -m'Add many files'
git push -u origin pr3
hub pull-request -m'Add many files03'


git checkout master
git checkout -b pr4
touch file{1..222}
git add .
git commit -m'Add many files'
git push -u origin pr4
hub pull-request -m'Add many files04'

git checkout master
git checkout -b pr5
touch file{a..d}{a..d}
touch aaaa bbbb cccc abc
git add .
git commit -m'Add many files'
git push -u origin pr5
hub pull-request -m'Add many files05'


if [[ -d mi-pyt-test-repo ]]; then
  rm -rf mi-pyt-test-repo
fi