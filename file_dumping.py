#!/usr/bin/env python
# coding: utf-8

# In[1]:


from glob import iglob
import os


# In[2]:


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
                
                    


# In[12]:


def main():
    base_dir= input("Please enter the directory: ")
    print("\n")
    repo_name = input("Please enter the repository name: ")
    print("\n")
    with os.scandir(base_dir) as entries:
        for entry in entries:
#             print(entry.name)
            if entry.name == "tox.ini":
#                 print("found tox")
                write_to_file(os.path.join(base_dir, entry.name), repo_name)
            if os.path.basename(os.path.normpath(base_dir)) == "tests":
                if not os.path.isdir(os.path.join(base_dir, entry)):
                    write_to_file(os.path.join(base_dir, entry.name), repo_name)


# In[40]:


main()


# In[ ]:




