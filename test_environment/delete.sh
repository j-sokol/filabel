#!/bin/bash -eu

echo "HTTP DELETE https://api.github.com/repos/${GH_USER}/mi-pyt-test-repo"
curl --header "Authorization: token ${GH_TOKEN}" -X DELETE https://api.github.com/repos/${GH_USER}/mi-pyt-test-repo


if [[ -d mi-pyt-test-repo ]]; then
	rm -rf mi-pyt-test-repo
fi