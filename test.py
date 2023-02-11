import os

#count files in result folder
dir_path = r'/Users/yayafung/Desktop/automated-gui-tester/result'
print(len([entry for entry in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, entry))]))