#!/usr/bin/env python
# coding: utf-8

# In[1]:


from glob import iglob
import os
from pathlib import Path


# In[2]:


def write_to_file(file_name, repo_name):
    with open(file_name, 'r') as file_content:
        content = file_content.read()
        name, extension = os.path.splitext(file_name)
        with open("dump_test_code_ansible.txt", 'a+') as file_append:
            file_append.write("===========Repository Name==========="+"\n")
            file_append.write(repo_name+"\n")
            file_append.write("===========File Path==========="+"\n")
            file_append.write(file_name+"\n")
            file_append.write("===========File Type==========="+"\n")
            file_append.write(extension+"\n")
            file_append.write("===========File Content==========="+"\n")
            file_append.write(content+"\n"+"\n"+"\n"+"\n")
                

                
        
        
def write_to_file_for_chef(file_name, repo_name):
    with open(file_name, 'r') as file_content:
        content = file_content.read()
        name, extension = os.path.splitext(file_name)
        with open("dump_test_code_chef.txt", 'a+') as file_append:
            file_append.write("===========Repository Name==========="+"\n")
            file_append.write(repo_name+"\n")
            file_append.write("===========File Path==========="+"\n")
            file_append.write(file_name+"\n")
            file_append.write("===========File Type==========="+"\n")
            file_append.write(extension+"\n")
            file_append.write("===========File Content==========="+"\n")
            file_append.write(content+"\n"+"\n"+"\n"+"\n")
                


# In[61]:


def main():
    base_dir= input("Please enter the directory: ")
    print("\n")
    repo_name = input("Please enter the repository name: ")
    print("\n")
    for (dirpath, dirnames, filenames) in os.walk(base_dir):
        for filename in filenames:
            if filename == "tox.ini":
                print
                write_to_file(os.path.join(base_dir, dirpath, filename), repo_name)
            
        for dirname in dirnames:
            if dirname == "tests":
                test_path = os.path.join(dirpath, dirname)
                print(test_path)
                for (testdirpath, testdirnames, testfilenames) in os.walk(test_path):
                    for testfile in testfilenames:
                        print(os.path.join(test_path,testdirpath, testfile))
                        write_to_file(os.path.join(test_path,testdirpath, testfile), repo_name)


# In[72]:


main()


# In[122]:


def find_bats(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.bats'):
                print(root)
           
                
def find_test_dirs(base_dir):
    test_dirs = list()
    for root, dirs, files in os.walk(base_dir):
        for dir in dirs:
            if dir.startswith('test'):
                test_dirs.append(root)
    return test_dirs

                
# find_bats(r"C:\Users\mehedi.md.hasan\PythonWorkspace\OSTK_CHEF\ostk-chef\compass-adapters\chef\cookbooks")


# In[120]:


def dump_chef_test_code():
    chef_repo_name = input("Enter the repo name:")
    base_dir_chef = input("Enter the base directory for chef project:")
    test_dirs = find_test_dirs(base_dir_chef)
    for test_dir in test_dirs:
        for root, dirnames, filenames in os.walk(test_dir):
            for dirname in dirnames:
                if dirname == "tests" or dirname == "test":
                    fullpath = os.path.join(root, dirname)
                    print(fullpath)
                    types = ('*.rb', '*.bats')
                    for t in types:
                        for path in Path(fullpath).rglob(t):
                            write_to_file_for_chef(str(path), chef_repo_name)
    for root, dirnames, filenames in os.walk(base_dir_chef):
        for filename in filenames:
            if filename.startswith('Rakefile'):
                path = os.path.join(root,filename)
                write_to_file_for_chef(str(path), chef_repo_name)

                        


# In[ ]:


dump_chef_test_code()

