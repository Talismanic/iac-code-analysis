#!/usr/bin/env python
# coding: utf-8

# In[188]:


#taken the code to fetch commits from below resources:
#https://gist.github.com/simonw/091b765a071d1558464371042db3b959


# get_commits function returns all the commit ids and the date of the commits of given directory


# In[189]:


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


# In[191]:


#finding the total number of commit in the project

lines = subprocess.check_output(
    ['git', 'log'], stderr=subprocess.STDOUT
).decode().split("\n")
leading_4_spaces = re.compile('^    ')
total_commit = get_commits(lines)
print("total commits in this project: " + str(len(total_commit)))


# In[192]:


import git
import os
g = git.Git('.')
# print(os.getcwd())
os.chdir(r"C:\Users\mehedi.md.hasan\PythonWorkspace\openstack-ansible\tests")
# print(os.getcwd())
lines_tests = g.log('.').splitlines()
test_script_commit = get_commits(lines_tests)
print("total commits in the test directory: " + str(len(test_script_commit)))


# In[202]:


# Percentage of test directory change:

print("test directory change frequency is " + str(len(test_script_commit)/len(total_commit)*100) + "%")


# In[ ]:




