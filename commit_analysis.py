#!/usr/bin/env python
# coding: utf-8

# In[314]:


#taken the code to fetch commits from below resources:
#https://gist.github.com/simonw/091b765a071d1558464371042db3b959


# get_commits function returns all the commit ids and the date of the commits of given directory
import subprocess 
import re
import elasticsearch
import io
from unidiff import PatchSet


# In[315]:


#Establishing ElasticSearch Connection with Bonsai
import os, base64, re, logging
from elasticsearch import Elasticsearch


es=Elasticsearch([{'host':'ec2-3-85-13-61.compute-1.amazonaws.com','port':9200}])


# Verify that Python can talk to ES (optional):
es.ping()


# In[316]:


#Parsing git commits of a repo
def get_commits(lines):
    commits = []
    current_commit = {}
    commit_summary = {}
    commit_output =[]
    
    def save_current_commit():
        title = current_commit['message'][0]
        message = current_commit['message'][1:]
        if message and message[0] == '':
            del message[0]
        current_commit["title"] = title
        current_commit["message"] = '\n'.join(message)
        commits.append(current_commit)

    for line in lines:
        if not line.startswith(' '):
            if line.startswith('commit '):
                if current_commit:
                    save_current_commit()
                    current_commit = {}
                current_commit["hash"] = str(line.split('commit ')[1])
               
            else:
                try:
                    key, value = line.split(':', 1)
                    current_commit[key.lower()] = value.strip()
                except ValueError:
                    pass
        else:
            current_commit.setdefault(
                'message', []
            ).append(leading_4_spaces.sub('', line))
    if current_commit:
        save_current_commit()
        
#     commits.sort(key = lambda c: c['date'], reverse=True)
    for commit in commits[:len(commits)]:
        commit_summary['hash'] = commit['hash']
        commit_summary['date'] = commit['date']
        commit_output.append(commit_summary.copy())
    commit_output.sort(key = lambda c: c['date'], reverse = True)
    
    return commit_output


# In[317]:


#finding the total number of commit in the project
os.chdir(r"C:\Users\mehedi.md.hasan\PythonWorkspace\openstack-ansible")
lines = subprocess.check_output(
    ['git', 'log'], stderr=subprocess.STDOUT
).decode().split("\n")
leading_4_spaces = re.compile('^    ')
total_commits = get_commits(lines)
print("total commits in this project: " + str(len(total_commits)))


# In[318]:


import git
import os
os.chdir(r"C:\Users\mehedi.md.hasan\PythonWorkspace\openstack-ansible\tests")

g = git.Git('.')
# print(os.getcwd())

# print(os.getcwd())
lines_tests = g.log('.').splitlines()
test_script_commits = get_commits(lines_tests)

print("total commits in the test directory: " + str(len(test_script_commits)))


# In[319]:


# Percentage of test directory change:

print("test directory change frequency is " + str(len(test_script_commits)/len(total_commits)*100) + "%")


# In[320]:


# finding the number of lines added & removed
# https://stackoverflow.com/questions/39423122/python-git-diff-parser


def tracking_files (commit_sha1):
    os.chdir(r"C:\Users\mehedi.md.hasan\PythonWorkspace\openstack-ansible")
    repo_directory_address = "."
    repository = git.Repo(repo_directory_address)
    ommit = repository.commit(commit_sha1)
    uni_diff_text = repository.git.diff(commit_sha1+ '~1', commit_sha1,
                                    ignore_blank_lines=True, 
                                    ignore_space_at_eol=True)
    patch_set = PatchSet(io.StringIO(uni_diff_text))
    lines_added = []
    lines_removed = []
    total_change={}
    for patched_file in patch_set:
        file_path = patched_file.path  # file name
        print('file name :' + file_path)
#         printing the added lines   
        for hunk in patched_file:
            for line in hunk:
                if line.is_added and line.value.strip() != '':
                    lines_added.append(str(line))
                if line.is_removed and line.value.strip() != '':
                    lines_removed.append(str(line))
        total_change['added'] = lines_added
        total_change['removed'] = lines_removed
        total_change['filename'] = file_path
        total_change['commit_id'] = commit_sha1
        res = es.index(index='iac_file_change',doc_type='filelog', body=total_change)
    
    return total_change
               

# print(tracking_files('c2d49cbff06f348acde42ad583a1401767e52806'))


# In[313]:


# Sending the changelog for each commit in the test folder to ES
test_commit_len = len(test_script_commits)
os.chdir(r"C:\Users\mehedi.md.hasan\PythonWorkspace\openstack-ansible")

for m in range(500,615):
    x = test_script_commits[m]['hash']
    file_changes = tracking_files(x)
    res = es.index(index='iac_file_change',doc_type='filelog',id=x,body=total_change)
#     print(file_changes)
#     differs_list = []
#     for differ in differs:
#         if differ not in differs_list:
#             if not differ.endswith(('.png','svg','wmf', 'ignore')):
              
#                 differs_list.append(differ)
#                 print(differ)
#                 changes = g.diff(differ, name_only=True)
#                 print (changes)


# In[ ]:




