
import time
from datetime import datetime
import zipfile
import sqlite3
import pathlib

__version__ = "0.1.4"

DT_FORMAT = "%Y-%m-%d %H:%M:%S"

def template_dest_path(location,name):
    location = pathlib.Path(location)
    return location / f"{name}.zip"

##########################
### Database Functions ###
##########################

def connect_to_db(db_path):
    db = sqlite3.connect(str(db_path))
    c = db.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS "templates" (
        "name" TEXT PRIMARY KEY,
        "created" REAL,
        "src_path" TEXT,
        "template_path" TEXT
    );""")
    return db

def name_exists(db,name):
    c = db.cursor()
    c.execute(
        "SELECT COUNT(*) FROM templates WHERE name = ?;",
        (name,)
    )
    return c.fetchone()[0] > 0

def get_template(db,name):
    c = db.cursor()
    c.execute("""
        SELECT created, src_path, template_path 
        FROM templates
        WHERE name = ?;""",(name,)
        )
    return c.fetchone()

def add_to_db(db,name,created,src,temp):
    c = db.cursor()
    c.execute("""
        INSERT INTO templates (
        name,created,src_path,template_path
        ) VALUES (?,?,?,?);""",
        (name,created,src,temp)
        )
    db.commit()

def update_db(db,name,created=None,src=None,temp=None):
    _created,_src,_temp = get_template(db,name)
    if created is None:
        created = _created
    if src is None:
        src = _src
    if temp is None:
        temp = _temp
    c = db.cursor()
    c.execute(
        """UPDATE templates SET 
          created = ?, 
          src_path = ?, 
          template_path = ?
        WHERE name = ?;""",
        (created,src,temp,name)
        )
    db.commit()

def del_from_db(db,name):
    c = db.cursor()
    c.execute(
        "DELETE FROM templates WHERE name = ?;",
        (name,))
    db.commit()

def count_templates(db):
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM templates;")
    return c.fetchone()[0]

def get_names(db):
    c = db.cursor()
    c.execute("SELECT name FROM templates;")
    return [n[0] for n in c.fetchall()]

def clear_db(db):
    c = db.cursor()
    c.execute("DELETE FROM templates;")
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
        dest_path = pathlib.Path(".").absolute()
    with zipfile.ZipFile(zip_path,'r') as zf:
        zf.extractall(dest_path)

def delete_file(file):
    file = pathlib.Path(file)
    file.unlink(missing_ok=True)


##########################
### Template Functions ###
##########################

def add_template(db,name,src_path,dest_path,created=None):
    if created is None: created = time.time()
    files = list_files(src_path)
    with zipfile.ZipFile(dest_path,'w') as zf:
        for f in files:
            zf.write(f)
    add_to_db(
        db,
        name,
        created,
        str(src_path.absolute()),
        str(dest_path.absolute())
        )

def del_template(db,name):
    _, _, template_path = get_template(
        db,
        name
        )
    del_from_db(db,name)
    delete_file(template_path)

def clear_templates(db):
    n = count_templates(db)
    r = input(
        f"About to in delete {n} templates. Are you sure you want to continue? [y/N]"
        ).strip().lower()
    if r in ['y','yes']:
        print("Deleting")
        all_names = get_names(db)
        for n in names:
            del_template(db,n)
    else:
        print("Canceled.")

def update_template(db,name,src_path,dest_path):
    created = time.time()
    files = list_files(src_path)
    with zipfile.ZipFile(dest_path,'w') as zf:
        for f in files:
            zf.write(f)
    update_db(
        db,
        name,
        created,
        str(src_path.absolute()),
        str(dest_path.absolute())
        )

def clone_template(db,name,path="."):
    assert(name_exists(db,name))
    _, _, template = get_template(db,name)
    template = pathlib.Path(template)
    with zipfile.ZipFile(template,"r") as zf:
        zf.extractall(path)

def list_templates(db):
    c = db.cursor()
    c.execute("""
        SELECT 
          name, 
          created,
          template_path
        FROM 
          templates;"""
          )
    data = c.fetchall()
    for i, r in enumerate(data):
        name, created, template_path = r
        data[i] = (
            name,
            datetime.fromtimestamp(
                created
            ).strftime(
                DT_FORMAT
            ),
            template_path
        )
    print("%-20s  %-20s  %-20s" % ("NAME","TIMESTAMP","SRC PATH"))
    for r in data:
        print("%-20s  %-20s  %s" % r)


def list_template_files(db,name):
    created, src, tmp = get_template(db,name)
    created = datetime.fromtimestamp(
        created
        ).strftime(
        DT_FORMAT
        )
    src = pathlib.Path(src)
    tmp = pathlib.Path(tmp)
    print(f"TEMPLATE: {name}")
    print(f"CREATED: {created}")
    print(f"SRC DIR: {src}")
    print(f"PATH: {tmp}")
    with zipfile.ZipFile(tmp,'r') as zf:
        contents = zf.namelist()
    print("CONTENTS:")
    for c in contents:
        print(f"\t{c}")


