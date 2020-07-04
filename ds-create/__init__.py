
import os
import argparse



def make_directories(tree):
    def make_dir_tree(parent,tree):
        for d, c in tree.items():
            path = os.path.join(parent,d)
            os.mkdir(path)
            if c: make_dir_tree(path,c)
    make_dir_tree(".",tree)


