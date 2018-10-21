import os

os.chdir('/Users/paulwainer/Paulthon/Scrap')

#print(os.getcwd())

for f in os.listdir():
    file_name, file_ext = os.path.splitext(f)
    
    if file_name[0:6] == 'scrap_':
        file_name = file_name[6:]
    new_name = file_name + file_ext
    
    os.rename(f, new_name)
