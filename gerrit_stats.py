#!/usr/bin/python

from email.mime.text import MIMEText
import json
import os
import pprint
import requests
import smtplib

import pdb

url_gerrithub = 'https://review.gerrithub.io/'
url_codeeng = os.environ['code_eng']
api_changes = 'changes/'
query_khaleesi_open = {'q': ['project:redhat-openstack/khaleesi', 'branch:master']}
query_khaleesi_settings_open = {'q': ['project:khaleesi-settings', 'branch:master']}
project_khaleesi = 'redhat-openstack/khaleesi'
project_khaleesi_settings = 'khaleesi-settings'
email_server = smtplib.SMTP(os.environ['smtp'], 25)


email_server.starttls()

def email_send(email_from, email_to, subject, body):
    #email = MIMEText(str(body))
    msg = MIMEText(str(body))
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject
    email_server.sendmail(email_from, email_to, msg.as_string())


def get_reviews(url, api_call, parameters=None):
  request = requests.get(url + api_call, parameters)
  result = json.loads(str(request.content[4:]))
  #pdb.set_trace()
  return result


def create_report(url, api, query, project):
  if 'gerrithub' in url:
    open_changes = get_reviews(url, api, query)[0]
  else:
    open_changes = get_reviews(url, api, query)[1]
  #pdb.set_trace()
  for change in open_changes:
      if change['status'] == 'NEW' and change['project'] == project:
        try:
          reviewers = get_reviews(url, api + change['change_id'] + '/reviewers/')
        except ValueError:
          continue
        for reviewer in reviewers:
          if reviewer['approvals']['Code-Review'].encode('utf-8').strip() != '0':
            if reviewer['name'] not in reviewers_count:
              reviewers_count[reviewer['name']] = 1
              reviewers_list[reviewer['name']] = []
              reviewers_list[reviewer['name']].append([change['project'], change['change_id'], change['subject']])
            else:
              reviewers_count[reviewer['name']] += 1
              reviewers_list[reviewer['name']].append([change['project'], change['change_id'], change['subject']])

def report(project):
  msg = ""
  msg += "Code Review Report: {0}\n".format(project)
  msg += "This is a list of engineers that have reviewed and voted on open gerrit reviews.\n"
  msg += "Please take time to review each others code!\n\n"

  for dev, count in reviewers_count.items():
      msg += "{0}: {1}\n".format(dev.encode('utf8'), count)

  msg += "\n\n"

  for dev, reviews in reviewers_list.items():
      msg += "DEVELOPER: {0}\n".format(dev.encode('utf8'))
      for item in reviews:
          item = [x.encode('utf-8') for x in item]
          msg += "    " + ", ".join(item) + "\n"
      msg += "\n\n"
  email_send(os.environ['REPORT_OWNER'], os.environ['REPORT_LIST'], project + ': gerrit reviews report', msg)

reviewers_count = {}
reviewers_list = {}
create_report(url_gerrithub, api_changes, query_khaleesi_open, project_khaleesi)
report(project_khaleesi)

reviewers_count = {}
reviewers_list = {}
create_report(url_codeeng, api_changes, query_khaleesi_settings_open, project_khaleesi_settings)
report(project_khaleesi_settings)
