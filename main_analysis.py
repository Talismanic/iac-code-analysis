#!/usr/bin/env python
# coding: utf-8

# In[203]:


from glob import iglob
import os
#from itertools import ifilter
import time
import array
from collections import Counter
import math
from math import sqrt
# from scipy import spatial


# In[173]:


#Calculating cosine similarity between two list
def counter_cosine_similarity(c1, c2):
    terms = set(c1).union(c2)
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
    return dotprod / (magA * magB)


# In[174]:


# Extracting leve 1 sub-directories of a given directory
def extract_directories(path):
    level = iglob(path)
    count = 0
    level_dirs = list()
    for x in level:
        if os.path.isdir(x):
            level_dirs.append(os.path.basename(x))
            count = count+1
#     print (level_dirs)
    return level_dirs


# In[195]:


# From the documents of Ansible and Chef we have  considered that all ansible project or chef project
# should have some standard in the base directory. Standard directories of ansible & chef has been
# kept in two list. Structure of the given project is compared with these list. The one with highest
# cosine similarity is considered as the winning project

def identify_project_type(path):

    ansible_l1_dir_list = ["ansible", "group_vars", "host_vars", "roles", "inventories", "playbooks", "inventory", "vars", "molecule"]
    chef_l1_dir_list = ["cookbooks", "data_bags", "policyfiles", "roles", "environments"]
    

    level1_dirs = extract_directories(path)
    print ("checking the project type from level 01 directories:" +"\n")
    
    ansible_l1_dirs_score = counter_cosine_similarity (Counter(level1_dirs), Counter(ansible_l1_dir_list))
    chef_l1_dirs_score = counter_cosine_similarity (Counter(level1_dirs), Counter(chef_l1_dir_list))
    
    if ansible_l1_dirs_score>chef_l1_dirs_score:
        project_type = "ansible"
    else:
        project_type = "chef"
        
    return project_type

    


# In[207]:


#location of any "test*", "tests*" directory is considered as the existence of testing
def is_test_available(base_dir):
    available = 0
    for dirpath, dirnames, filenames in os.walk(base_dir):
        for dirname in dirnames:
            if "test" in dirname or "tests" in dirname :
                available = 1
                print("test folder location: " + dirpath)
    
    return available


# In[208]:


def is_molecule_available(base_dir):
    available = 0
    for dirpath, dirnames, filenames in os.walk(base_dir):
        for dirname in dirnames:
            if "molecule" in dirname:
                available = 1
    return available


# In[209]:


def is_vcs_used(base_dir):
    available = 0
    for dirpath, dirnames, filenames in os.walk(base_dir):
        for filename in filenames:
            if ".git" in filename:
                available = 1
    return available


# In[210]:


def is_ci_used(base_dir):
    available = 0
    for dirpath, dirnames, filenames in os.walk(base_dir):
        for filename in filenames:
            if "travis" in filename or "jenkins" in filename:
                available = 1
    return available


# In[211]:


input_dir = input("Enter the directory Name:")
cur_dir = os.getcwd() + "\\" +input_dir +"\\*"
# curDir2 = os.path.join(os.getcwd(), inputDir)
print(cur_dir)
print ("Analyzing level 01:")
time.sleep(1)

#finding all folder names of level 1

project_type = identify_project_type(cur_dir)
print("Determined project type is : " + project_type)
time.sleep(1)

print("Checking whether a test directory is available: ")

if (is_test_available(os.getcwd() + "\\"+input_dir)) == 1:
    print("Test folder available")
else:
    print("No test folder found. Aborting....")

time.sleep(1)

print("Checking the use of test framework: ")

if (is_molecule_available(os.getcwd() + "\\"+input_dir)==1):
    print("Molecule framework has been used")
else:
    print("Molecule framework has not been used")
    

print("Checking the use of version control system: ")

if (is_vcs_used(os.getcwd() + "\\"+input_dir)==1):
    print("Version Control System has been used")
else:
    print("Version Control System has not been used")
    

    
    
print("Checking the use of CI system: ")

if (is_ci_used(os.getcwd() + "\\"+input_dir)==1):
    print("CI  System has been used")
else:
    print("CI System has not been used")


# In[212]:


###
# Repos:
#      https://github.com/chef-cookbooks/docker
#     https://github.com/gtmanfred/chef-repo
#     https://github.com/facebook/chef-cookbooks
#     https://github.com/rcbops/chef-cookbooks
#     https://github.com/enginyoyen/ansible-best-practises
#     https://github.com/cleveritcz/auto-molecule
#     https://github.com/geerlingguy/ansible-for-devops
#     https://github.com/openstack/ansible-role-container-registry
#     https://github.com/openstack/ansible-role-python_venv_build
#     https://github.com/openstack/ansible-role-systemd_mount.git
#     https://github.com/openstack/ansible-role-systemd_networkd.git
#     https://github.com/openstack/ansible-role-tripleo-modify-image.git
#     https://github.com/openstack/bifrost.git
#     https://github.com/cloud-bulldozer/browbeat.git
#     https://coderwall.com/p/lz0uva/find-all-files-modified-between-commits-in-git


# In[213]:


###Important git commands
## find all logs
#git log

## find the change history of a file
#gitk filename


## View git history of a folder
#git log -- path/to/folder


## find the files changed between two commits
#git diff --name-only start_commit_sha end_commit_sha



# In[ ]:




