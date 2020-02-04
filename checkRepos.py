#!/usr/bin/env python

import json
import subprocess
import time

# For a user search
orgOrUser = "users"
orgOrUserName = "cookpa"

# for an org search
# orgOrUser = "orgs"
# orgOrUserName = "pennBBL"


# Github limits to 100 results per page, so if you have more than 100 repos, you will need to set this
# This is a hack, it would be better to figure this out automatically by calling curl -I and parsing the page info
numPages=1

for page in range(numPages):
  curlCmd = "curl https://api.github.com/" + orgOrUser + "/" + orgOrUserName + "/repos?page=" + str(page+1) + "\&per_page=100 > " + orgOrUserName + ".json"
  print("Getting repos with: " + curlCmd)
  ex = subprocess.Popen(curlCmd, shell = True).wait()
  jData = open(orgOrUserName + ".json").read()

  repoData = json.loads(jData)

  for repo in repoData:
    repoName = repo['name']
    thCmd = "trufflehog --rules rules.json --regex --entropy FALSE https://github.com/" + orgOrUserName + "/" + repoName
    print("Checking " + repoName)
    ex = subprocess.Popen(thCmd, shell = True).wait()
    time.sleep(5)


