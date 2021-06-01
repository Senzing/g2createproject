#! /usr/bin/env python3

import sys
import os
import argparse
import errno
import shutil

# Folders to copy from
senzing_paths = [
    '/opt/senzing',
    '/etc/opt/senzing',
    '/var/opt/senzing'
]

# files to update
files_to_update = [
    'setupEnv',
    'etc/G2Module.ini',
    'etc/G2Project.ini'
]

def find_replace_in_file(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()

    # Safely write the changed content, if found in the file
    with open(filename, 'w') as f:
        s = s.replace(old_string, new_string)
        f.write(s)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a per-user instance of Senzing in a new folder with the specified name.')
    parser.add_argument('folder', metavar='F', nargs='?', default='~/senzing', help='the name of the folder to create (default is "~/senzing"). It must not already exist')
    args = parser.parse_args()

    target_path = os.path.normpath(os.path.join(os.getcwd(), os.path.expanduser(args.folder)))
    
    # check if folder exists. It shouldn't
    if os.path.exists(target_path) or os.path.isfile(target_path):
        print('"' + target_path + '" already exists or is a path to a file. Please specify a folder that does not already exist.')
        sys.exit(1)

    for path in senzing_paths:
        if target_path.startswith(path):
            print('Project cannot be created at "' + target_path + '". Projects cannot be created in these paths: ' + ",".join(senzing_paths))
            sys.exit(1)

    print("Creating Senzing instance at " + target_path )
    
    # copy opt
    shutil.copytree('/opt/senzing/g2', target_path)
    
    # copy etc to etc and resources/templates
    shutil.copytree('/etc/opt/senzing', os.path.join(target_path, 'etc'))
    shutil.copytree('/etc/opt/senzing', os.path.join(target_path, 'resources/templates'))

    # copy var
    shutil.copytree('/var/opt/senzing', os.path.join(target_path, 'var'))
    
    # soft link in data
    os.symlink('/opt/senzing/data/1.0.0', os.path.join(target_path, 'data'))

    # rename the template files to the real names
    path_to_update = os.path.join(target_path, 'etc')

    for file in os.listdir(path_to_update):
        if file.endswith('.template'):
            os.rename(os.path.join(path_to_update, file), os.path.join(path_to_update, file).replace('.template',''))

    # paths to substitute
    senzing_path_subs = [
        ('/opt/senzing/g2', target_path),
        ('/opt/senzing/data', os.path.join(target_path, 'data')),
        ('/etc/opt/senzing', os.path.join(target_path, 'etc')),
        ('/var/opt/senzing', os.path.join(target_path, 'var')),
        ('/opt/senzing', target_path)        
    ]

    for f in files_to_update:
        for p in senzing_path_subs:
            # Anchor the replace on the character that comes before the path. This ensures that we are only 
            # replacing the begining of the path and not a substring of the path.
            find_replace_in_file(os.path.join(target_path, f), '=' + p[0], '=' + os.path.join(target_path, p[1]))
            find_replace_in_file(os.path.join(target_path, f), '@' + p[0], '@' + os.path.join(target_path, p[1]))

