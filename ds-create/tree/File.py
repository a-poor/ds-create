
import os

from .Folder import Folder

class File:
    def __init__(self,name,parent=None,path=".",contents=""):
        self.name = name
        self.parent = parent
        self.path = path
        self.contents = contents

