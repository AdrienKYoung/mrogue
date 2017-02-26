from distutils.core import setup
import py2exe
import zipfile, os

project_name = "roguelike-prealpha"
version = "0.1.0"
dependencies = ['SDL2.dll','libtcod.dll','libtcod-gui.dll','terminal16x16_gs_ro.png','menu_background.png','features.txt']

setup(
    version=version,
    data_files=[('.',dependencies)],
    console=['main.py'],
    zipfile=None,
    options = {
        "build": {"build_base":"build"},
        'py2exe': {
        #"optimize": 2,
        "compressed": True,
        "bundle_files": 1
      }}
)

arc_exclude = ['w9xpopen.exe']

target = zipfile.ZipFile("{}-{}.zip".format(project_name,version),"w")
for dirname, _, files in os.walk("dist"):
    for f in files:
        if f not in arc_exclude:
            target.write(os.path.join(dirname,f),f)
target.close()

for dirname, _, files in os.walk("."):
    for f in files:
        if ".pyc" in f:
            os.remove(os.path.join(dirname,f))