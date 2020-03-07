#!/usr/bin/env python
# coding: utf-8

# In[110]:


#taken the code to fetch commits from below resources:
#https://gist.github.com/simonw/091b765a071d1558464371042db3b959


# get_commits function returns all the commit ids and the date of the commits of given directory
import subprocess 
import re
import elasticsearch
import io
from unidiff import PatchSet
import time
import datetime


# In[155]:


#Establishing ElasticSearch Connection with Bonsai
import os, base64, re, logging
from elasticsearch import Elasticsearch


es=Elasticsearch([{'host':'ec2-3-85-13-61.compute-1.amazonaws.com','port':9200}])


# Verify that Python can talk to ES (optional):
es.ping()


# In[156]:


base_path = r"C:\Users\mehedi.md.hasan\PythonWorkspace\browbeat"
test_path = r"C:\Users\mehedi.md.hasan\PythonWorkspace\browbeat\tests"
project_name = "browbeat"


# In[157]:


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


# In[158]:


#finding the total number of commit in the project
os.chdir(base_path)
lines = subprocess.check_output(
    ['git', 'log'], stderr=subprocess.STDOUT
).decode().split("\n")
leading_4_spaces = re.compile('^    ')
total_commits = get_commits(lines)
print(total_commits[0])
print("total commits in this project: " + str(len(total_commits)))


# In[159]:


import git
import os
os.chdir(test_path)

g = git.Git('.')
# print(os.getcwd())

# print(os.getcwd())
lines_tests = g.log('.').splitlines()
test_script_commits = get_commits(lines_tests)

print("total commits in the test directory: " + str(len(test_script_commits)))


# In[160]:


# Percentage of test directory change:

print("test directory change frequency is " + str(len(test_script_commits)/len(total_commits)*100) + "%")


# In[161]:


test_line1 = "ceph_mons: \"{{ groups[mon_group_name]\n"
test_line2 = "%%^82773a"

def searchForMatch(test_line):
    searchObj = re.search(r'(\S+): (([A-Za-z]|[0-9]|_|"|{|\[| |\]|}|:|\/|.|\=)+$)', test_line)
    if searchObj:
        return True
    else:
        return False


# In[162]:


#this function will:
#return 0 is the line is a comment
#return 1 if the file is not an yaml or python file
#retunr 2 if the line does not contain the pattern
#return 3 if the line contains a property name
def check_for_property_change(s, filename):
    if s.startswith('#'):
        return 0;
    else:
#         print("Non comment")
        if (filename.endswith(".yml")) or (filename.endswith(".yaml")) or (filename.endswith(".py")) or (filename.endswith(".j2"))  :
            if searchForMatch(s):
                return 3
            else:
                return 2                
            
        else:
            return 1
            
        
    


# In[163]:


# finding the number of lines added & removed
# https://stackoverflow.com/questions/39423122/python-git-diff-parser


def tracking_files (commit_sha1, commit_date, project_name):
    os.chdir(base_path)
    repo_directory_address = "."
    repository = git.Repo(repo_directory_address)
    commit = repository.commit(commit_sha1)
    uni_diff_text = repository.git.diff(commit_sha1+ '~1', commit_sha1,
                                    ignore_blank_lines=True, 
                                    ignore_space_at_eol=True)
    patch_set = PatchSet(io.StringIO(uni_diff_text))
    lines_added = []
    lines_removed = []
    total_change={}
    for patched_file in patch_set:
        property_change = 0
        file_path = patched_file.path  # file name
        print('file name :' + file_path)
        if not file_path.endswith(('.png','.svg','.wmf', '.ignore', '.rst', '.md')):
            print("Entered in hunk loop")
            for hunk in patched_file:
                for line in hunk:
                    if line.is_added and line.value.strip() != '':
                        last_added_line = str(line).strip('+')    
                        if check_for_property_change(last_added_line, file_path) == 3:
                            lines_added.append(last_added_line)                  
                            property_change = 1
                    if line.is_removed and line.value.strip() != '':
                        last_removed_line = str(line).strip('-')    
                        if check_for_property_change(last_removed_line, file_path) == 3:
                            property_change = 1
                            lines_added.append(last_removed_line)
            total_change['added'] = lines_added
            total_change['removed'] = lines_removed
            total_change['filename'] = file_path
            total_change['commit_id'] = commit_sha1
            total_change['has_property_changed'] = property_change
            total_change['commit_timestamp'] = time.mktime(datetime.datetime.strptime(commit_date, "%a %b %d %H:%M:%S %Y %z").timetuple())
            total_change['project_name'] = project_name
            res = es.index(index='iac_file_change',doc_type='filelog', body=total_change)
    
    return total_change
               
# print(tracking_files('c2d49cbff06f348acde42ad583a1401767e52806'))


# In[164]:


# Sending the changelog for each commit in the test folder to ES
test_commit_len = len(test_script_commits)
os.chdir(base_path)

for m in range(0,614):
    x = test_script_commits[m]['hash']
    commit_date = test_script_commits[m]['date']
#     project_name = "bifrost"
    file_changes = tracking_files(x, commit_date, project_name)
    print(m)
    
#     res = es.index(index='iac_file_change',doc_type='filelog', body=file_changes)
#     res = es.index(index='iac_file_change',doc_type='filelog',id=x,body=total_change)
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


#unit test for check_for_property_change
s1 =  "# so we have to feed it a list of IPs\n"
s2 = "octavia_v2: True\n"
s3 = "ceph_mons: \"{{ groups[mon_group_name]\n"
f = "tests/roles/bootstrap-host/vars/main.yml"
# if f.endswith(".yml", "yaml"):
#     print("hellp")
# s1 = str(s1)
check_for_property_change(s2, f)
commit_sha1= "c2d49cbff06f348acde42ad583a1401767e52806"

# repo = git.Repo(".")
# commits = list(repo.iter_commits("master", max_count=5))
# print(dir(commits[0]))


# In[33]:


fileName = "doc/source/developer-docs/inventory.rst"
print(fileName)
if not fileName.endswith(('.png','.svg','.wmf', '.ignore', '.rst', '.md')):
    print("file not static")
  


# In[82]:



s = "Wed Sep 21 12:24:30 2016 +0200"
time.mktime(datetime.datetime.strptime(s, "%a %b %d %H:%M:%S %Y %z").timetuple())
# s = "Wed Sep 12 12:24:30 2011 +0200"
# time.mktime(datetime.datetime.strptime(s, "%a %b %d %H:%M:%S %Y %z").timetuple())


# In[112]:


(\S+): (([A-Za-z]|[0-9]|_|"|{|\[| |\]|}|:|\/|.|\=)+$)


# In[ ]:




