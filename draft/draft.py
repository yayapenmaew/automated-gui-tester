import os

# Path to the first folder
folder1_path = '/Users/yayafung/Desktop/automated-gui-tester/apk'

# Path to the second folder
folder2_path = '/Users/yayafung/Desktop/FlowDroid/apk'

# Get a list of all the files in folder1
folder1_files = os.listdir(folder1_path)

# Get a list of all the files in folder2
folder2_files = os.listdir(folder2_path)
count = 0

# Loop through the files in folder1
for file1 in folder1_files:
    # Check if the file is also in folder2
    if file1 in folder2_files:
        # If it is, delete the file from folder1
        os.remove(os.path.join(folder1_path, file1))
        count += 1

print(count)