import os

exclude = ['env', '__pycache__', 'site-packages', '.git', '.idea', '.vscode', 'migrations']

def print_tree(start_path='.', indent=''):
    for item in sorted(os.listdir(start_path)):
        path = os.path.join(start_path, item)
        if any(x in path for x in exclude):
            continue
        print(indent + '|-- ' + item)
        if os.path.isdir(path):
            print_tree(path, indent + '|   ')

print("Project Structure:\n")
print_tree('.')
