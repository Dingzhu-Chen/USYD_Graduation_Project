import os

# PUT ME IN THE WEB FOLDER

dir_path = os.path.dirname(os.path.realpath(__file__))

for subdir, dirs, files in os.walk(dir_path, followlinks=False, topdown=False):
    if os.path.basename(subdir) == 'migrations':  # Check for 'migrations' folder in cross-platform way
        for file in files:
            if file != '__init__.py':
                filepath = os.path.join(subdir, file)
                print(filepath)
                os.remove(filepath)