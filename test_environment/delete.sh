#!/bin/bash -eu

echo "HTTP DELETE https://api.github.com/repos/${GH_USER}/mi-pyt-test-repo"
curl --header "Authorization: token ${GH_TOKEN}" -X DELETE https://api.github.com/repos/${GH_USER}/mi-pyt-test-repo


for I in {1..4}; do
  echo "HTTP DELETE https://api.github.com/repos/${GH_USER}/filabel-testrepo${I}"
  curl --header "Authorization: token ${GH_TOKEN}" -X DELETE https://api.github.com/repos/${GH_USER}/filabel-testrepo${I}
done
