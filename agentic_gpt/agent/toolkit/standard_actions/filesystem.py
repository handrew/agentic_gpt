"""Helpful function for the agent to interact with the filesystem.

For now do not allow any actions that could be destructive."""
import os


def get_file_contents(filename):
    """Reads file into memory."""
    with open(filename, 'r') as f:
        return {"context": f.read()}

def list_dir(path):
    """Lists the contents of a directory."""
    return {"context": os.listdir(path)}

def mkdir(path):
    """Creates a directory."""
    os.mkdir(path)
    return {"context": "Created directory: {}".format(path)}

def touch(path):
    """Creates a file."""
    with open(path, 'w') as f:
        f.write("")
    return {"context": "Created file: {}".format(path)}

def write(path, contents):
    """Writes to a file."""
    with open(path, 'w') as f:
        f.write(contents)
    return {"context": "Wrote to file: {}".format(path)}

def append(path, contents):
    """Appends to a file."""
    with open(path, 'a') as f:
        f.write(contents)
    return {"context": "Appended to file: {}".format(path)}
