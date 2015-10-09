#!/usr/bin/python3

import requests
import json

import pdb

url = 'https://review.gerrithub.io/'
api_changes = 'changes/'
query_khaleesi_open = {'q': ['owner:weshayutin', 'status:open', 'project:redhat-openstack/khaleesi', 'branch:master']}


reviewers_dict = {}

def get(url, api_call, parameters=None):
  request = requests.get(url + api_call, parameters)
  print(request.url)
  return json.loads(request.content[4:])


open_changes = get(url, api_changes, query_khaleesi_open)

print(len(open_changes[0]))
for change in open_changes[0]:
    if change['status'] == 'NEW':
      print("{0} {1} {2} {3}".format(change['status'], change['change_id'], change['project'], change['subject']))
      reviewers = get(url, api_changes + change['change_id'] + '/reviewers/')
      for reviewer in reviewers:
        if reviewer['name'] not in reviewers_dict:
          reviewers_dict[reviewer['name']] = 1
        else:
          reviewers_dict[reviewer['name']] += 1

print(reviewers_dict)


