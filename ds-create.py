
import time
from datetime import datetime
import zipfile
import sqlite3
import pathlib
import argparse

# Defaults
DSC_HOME = "~/ds-create/"
DT_FORMAT = "%Y-%m-%d %H:%M:%S"



# Get pathlib paths
dsc_home = pathlib.Path(DSC_HOME).expanduser()
dsc_db_path = dsc_home / "dsc-templates.db"
dsc_templates = dsc_home / "templates/"

# Make if doesn't exist
dsc_home.mkdir(exist_ok=True)
dsc_templates.mkdir(exist_ok=True)

# Connect to the database
db = sqlite3.connect(dsc_db_path)
c = db.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS "templates" (
    "name" TEXT PRIMARY KEY,
    "created" REAL,
    "src_path" TEXT,
    "template_path" TEXT
);""")


##########################
### Database Functions ###
##########################

def name_exists(name):
    c.execute(
        "SELECT COUNT(*) FROM templates WHERE name = ?;",
        (name,)
    )
    return c.fetchone()[0] > 0

def get_template(name):
    c.execute("""
        SELECT created, src_path, template_path 
        FROM templates
        WHERE name = ?;""",(name,)
        )
    return c.fetchone()

def add_to_db(name,created,src,temp):
    c.execute("""
        INSERT INTO templates (
        name,created,src_path,template_path
        ) VALUES (?,?,?,?);""",
        (name,created,src,temp)
        )
    db.commit()

def update_db(name,created=None,src=None,temp=None):
    _created,_src,_temp = get_template(name)
    if created is None:
        created = _created
    if src is None:
        src = _src
    if temp is None:
        temp = _temp
    c.execute(
        """UPDATE templates SET 
          created = ?, 
          src_path = ?, 
          template_path = ?
        WHERE name = ?;""",
        (created,src,temp,name)
        )
    db.commit()

def del_from_db(name):
    c.execute(
        "DELETE FROM templates WHERE name = ?;",
        (name,))
    db.commit()

####################################
### File Manipulation Functions  ###
####################################

def list_files(path="."):
    return list(pathlib.Path(path).rglob("*"))

def zip_folder(src_path,dest_path):
    files = list_files(src_path)
    with zipfile.ZipFile(dest_path,'w') as zf:
        for f in files:
            zf.write(f)

def unzip_folder(zip_path,dest_path=None):
    if dest_path is None:
        dest_path = pathlib.Path(".")
    with zipfile.ZipFile(zip_path,'r') as zf:
        zf.extractall(dest_path)

##########################
### Template Functions ###
##########################

def add_template(name,path=".",created=None):
    if created is None: created = time.time()
    src_path = pathlib.Path(path)
    dst_path = dsc_templates / f"{name}.zip"
    files = list_files(src_path)
    with zipfile.ZipFile(dst_path,'w') as zf:
        for f in files:
            zf.write(f)
    add_to_db(
        name,
        created,
        str(src_path),
        str(dst_path)
        )

def del_template(name):
    del_from_db(name)

def update_template(name,path="."):
    created = time.time()
    src_path = pathlib.Path(path)
    dst_path = dsc_templates / f"{name}.zip"
    files = list_files(src_path)
    with zipfile.ZipFile(dst_path,'w') as zf:
        for f in files:
            zf.write(f)
    update_db(
        name,
        created,
        str(src_path),
        str(dst_path)
        )

def clone_template(name,path="."):
    assert(name_exists(name))
    _, _, template = get_template(name)
    template = pathlib.Path(template)
    with zipfile.ZipFile(template,"r") as zf:
        zf.extractall(path)

def list_templates():
    c.execute("""
        SELECT 
          name, 
          created, 
          src_path, 
          template_path 
        FROM 
          templates;"""
          )
    data = c.fetchall()
    for i, r in enumerate(data):
        data[i][1] = datetime.fromtimestamp(
            r[1]
        ).strftime(
            DT_FORMAT
        )
    print(" %20s | %19s" % ("NAME","TIMESTAMP"))
    print(" %s+%s" % ("-"*22,"-"*21))
    for r in data:
        print("%20s | %19s" % (r[0],r[1]))

def list_template_files(name):
    created, src, tmp = get_template(name)
    created = datetime.fromtimestamp(
        created
        ).strftime(
        DT_FORMAT
        )
    src = pathlib.Path(src)
    tmp = pathlib.Path(src)
    print(f"TEMPLATE: {name}")
    print(f"CREATED: {created}")
    print(f"SRC DIR: {src}")
    print(f"PATH: {tmp}")
    with zipfile.ZipFile(tmp,'r') as zf:
        contents = zf.namelist()
    print("CONTENTS:")
    for c in contents:
        print(f"\t{c}")


#######################
### Argument Parser ###
#######################

parser = argparse.ArgumentParser(
    prog="ds-create",
    description="CLI to save app templates."
)
parser.add_argument(
    "cmd",
    default="",
    choices=['snap','create','update','delete','list'],
    help="Template operation to perform"
)
parser.add_argument(
    "-n",
    "--name",
    dest="name",
    default=None,
    help="Name of template to use for cmd."
)

# Commands:
# 1 - take snapshot of this directory. use name foo
# 2 - unzip saved template, foo
# 3 - update template foo
# 4 - delete template foo
# 5 - list all templates
# 6 - list info for specific template
#
# everything needs (cmd, name) except 5


# Get & clean arguments
args = parser.parse_args()
cmd = args.cmd.strip().lower()
if args.name is None:
    name = None
else:
    name = args.name.strip().lower()

# Choose an action
if cmd == "snap":
    assert name is not None, "Must supply name for new template"
    assert not name_exists(name), f"Name \"{name}\" already exists. To update use cmd \"update\""
    
    print(f"Saving template \"{name}\"")
    add_template(name)

elif cmd == "create":
    assert name_exists(name), f"Couldn't find template \"{name}\""
    
    print(f"Cloning template \"{name}\"")
    clone_template(name)

elif cmd == "update":
    assert name_exists(name), f"Couldn't find template \"{name}\""
    
    print(f"Updating template \"{name}\"")
    update_template(name)

elif cmd == "delete":
    assert name_exists(name), f"Couldn't find template \"{name}\""
    
    print(f"Deleting template \"{name}\"")
    del_template(name)

elif cmd == "list":
    if name is None:
        list_templates()
    else:
        assert name_exists(name), f"Couldn't find template \"{name}\""
        list_template_files(name)

else:
    raise Exception(f"Error: Didn't understand command \"{cmd}\"")




