import zipfile
import os
# z = zipfile.ZipFile("media_files.zip", 'r')
#
# list_files = list()
# for name in z.namelist():
#     print(name)
#     list_files.append(name)
#
#     z.extract(name)
#     os.rename(name, name.encode())
# os.removedirs(list_files[0])

a = "Ёжик"
b = a.encode('utf-8')
print(b)