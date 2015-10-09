#!/usr/bin/python3

import requests
import json
import pprint

import pdb

url = 'https://review.gerrithub.io/'
api_changes = 'changes/'
query_khaleesi_open = {'q': ['project:redhat-openstack/khaleesi', 'branch:master']}


reviewers_count = {}
reviewers_list = {}


def get(url, api_call, parameters=None):
  request = requests.get(url + api_call, parameters)
  return json.loads(request.content[4:])


open_changes = get(url, api_changes, query_khaleesi_open)

print(len(open_changes[0]))
for change in open_changes[0]:
    if change['status'] == 'NEW':
      #print("{0} {1} {2} {3}".format(change['status'], change['change_id'], change['project'], change['subject']))
      try:
        reviewers = get(url, api_changes + change['change_id'] + '/reviewers/')
      except ValueError:
        print('Invalid value found')
        continue
      for reviewer in reviewers:
        if reviewer['name'] not in reviewers_count:
          reviewers_count[reviewer['name']] = 1
          reviewers_list[reviewer['name']] = []
          reviewers_list[reviewer['name']].append([change['project'], change['change_id'], change['subject']])
        else:
          reviewers_count[reviewer['name']] += 1
          reviewers_list[reviewer['name']].append([change['project'], change['change_id'], change['subject']])

for dev, count in reviewers_count.items():
    print("{0}: {1}").format(dev.encode('utf8'), count)

print("\n\n")

for dev, reviews in reviewers_list.items():
    print("DEVELOPER: {0}").format(dev.encode('utf8'))
    for item in reviews:
        item = [x.encode('utf-8') for x in item]
        print("    {0}").format(item)
    print("\n")


