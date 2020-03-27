#!/usr/bin/env python
# coding: utf-8

# In[48]:


from glob import iglob
import os


# In[49]:


# base_dir = os.getcwd()
base_dir=r"C:\Users\mehedi.md.hasan\PythonWorkspace\openstack-ansible\tests"
print(base_dir)
repo_name = "test_repo"



# In[52]:


def write_to_file(file_name, repo_name):
    with open(file_name, 'r') as file_content:
        content = file_content.read()
        name, extension = os.path.splitext(file_name)
        with open("dump_test_code.txt", 'a+') as file_append:
            file_append.write("===========Repository Name==========="+"\n")
            file_append.write(repo_name+"\n")
            file_append.write("===========File Path==========="+"\n")
            file_append.write(file_name+"\n")
            file_append.write("===========File Type==========="+"\n")
            file_append.write(extension+"\n")
            file_append.write("===========File Content==========="+"\n")
            file_append.write(content+"\n"+"\n"+"\n"+"\n")
                
                    


# In[54]:


def main():
    base_dir= input("Please enter the directory: ")
    print("\n")
    repo_name = input("Please enter the repository name: ")
    print("\n")
    with os.scandir(base_dir) as entries:
        for entry in entries:
            if not os.path.isdir(os.path.join(base_dir, entry)):
#                 print(os.path.join(base_dir, entry.name))
                write_to_file(os.path.join(base_dir, entry.name), repo_name)


# In[56]:


main()


# In[ ]:




