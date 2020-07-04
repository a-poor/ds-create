
import os

from .File import File

class Folder:
    def __init__(self,name,parent=None,path=".",children=[]):
        self.name = name
        self.parent = parent
        self.path = path
        self.children = children

