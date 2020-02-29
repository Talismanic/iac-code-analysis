#!/usr/bin/env python
# coding: utf-8

# In[127]:


#taken the code to fetch commits from below resources:
#https://gist.github.com/simonw/091b765a071d1558464371042db3b959


# get_commits function returns all the commit ids and the date of the commits of given directory
import subprocess 
import re
import elasticsearch
import io
from unidiff import PatchSet


# In[128]:


#Establishing ElasticSearch Connection with Bonsai
import os, base64, re, logging
from elasticsearch import Elasticsearch


es=Elasticsearch([{'host':'ec2-3-85-13-61.compute-1.amazonaws.com','port':9200}])


# Verify that Python can talk to ES (optional):
es.ping()


# In[129]:


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


# In[130]:


#finding the total number of commit in the project
os.chdir(r"C:\Users\mehedi.md.hasan\PythonWorkspace\openstack-ansible")
lines = subprocess.check_output(
    ['git', 'log'], stderr=subprocess.STDOUT
).decode().split("\n")
leading_4_spaces = re.compile('^    ')
total_commits = get_commits(lines)
print("total commits in this project: " + str(len(total_commits)))


# In[131]:


import git
import os
os.chdir(r"C:\Users\mehedi.md.hasan\PythonWorkspace\openstack-ansible\tests")

g = git.Git('.')
# print(os.getcwd())

# print(os.getcwd())
lines_tests = g.log('.').splitlines()
test_script_commits = get_commits(lines_tests)

print("total commits in the test directory: " + str(len(test_script_commits)))


# In[132]:


# Percentage of test directory change:

print("test directory change frequency is " + str(len(test_script_commits)/len(total_commits)*100) + "%")


# In[133]:


test_line1 = "ceph_mons: \"{{ groups[mon_group_name]\n"
test_line2 = "%%^82773a"

def searchForMatch(test_line):
    searchObj = re.search(r'(\S+): (([A-Za-z]|[0-9]|_|"|{|\[| |\]|}|:|\/|.|\=)+$)', test_line)
    if searchObj:
        return True
    else:
        return False


# In[137]:


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
            
        
    


# In[138]:


# finding the number of lines added & removed
# https://stackoverflow.com/questions/39423122/python-git-diff-parser


def tracking_files (commit_sha1):
    os.chdir(r"C:\Users\mehedi.md.hasan\PythonWorkspace\openstack-ansible")
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
        file_path = patched_file.path  # file name
        print('file name :' + file_path)
        property_change = 0
#         printing the added lines

        for hunk in patched_file:
            for line in hunk:
                if line.is_added and line.value.strip() != '':
                    last_added_line = str(line).strip('+')    
                    lines_added.append(last_added_line)
                    if check_for_property_change(last_added_line, file_path) == 3:
                        property_change = 1
                if line.is_removed and line.value.strip() != '':
                    last_removed_line = str(line).strip('-')    
                    lines_added.append(last_removed_line)
                    if check_for_property_change(last_removed_line, file_path) == 3:
                        property_change = 1
                        
                        
        total_change['added'] = lines_added
        total_change['removed'] = lines_removed
        total_change['filename'] = file_path
        total_change['commit_id'] = commit_sha1
        total_change['has_property_changed'] = property_change
        res = es.index(index='iac_file_change',doc_type='filelog', body=total_change)
    
    return total_change
               

# print(tracking_files('c2d49cbff06f348acde42ad583a1401767e52806'))


# In[ ]:


# Sending the changelog for each commit in the test folder to ES
test_commit_len = len(test_script_commits)
os.chdir(r"C:\Users\mehedi.md.hasan\PythonWorkspace\openstack-ansible")

for m in range(50,614):
    x = test_script_commits[m]['hash']
    file_changes = tracking_files(x)
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


# In[119]:


#unit test for check_for_property_change
s1 =  "# so we have to feed it a list of IPs\n"
s2 = "      dest: user_variables_congress.yml\n"
s3 = "ceph_mons: \"{{ groups[mon_group_name]\n"
f = "get-ansible-role-requirements.yaml"
# if f.endswith(".yml", "yaml"):
#     print("hellp")
# s1 = str(s1)
check_for_property_change(s2, f)


# In[111]:





# In[112]:


(\S+): (([A-Za-z]|[0-9]|_|"|{|\[| |\]|}|:|\/|.|\=)+$)


# In[ ]:




