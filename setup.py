#part of mrogue, an interactive adventure game
#Copyright (C) 2017 Adrien Young and Tyler Soberanis
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
import py2exe
import zipfile, os

project_name = "mrogue-prealpha"
version = "0.1.3"

dependencies = ['SDL2.dll','libtcod.dll',
                'terminal16x16_gs_ro.png','menu_background.png','features.txt',
                'legal/COPYING','legal/LIBTCOD-LICENSE.txt','legal/MROGUE-LICENSE.txt']

features = ['features/branch-gates.txt','features/features-badlands.txt','features/features-forest.txt',
                'features/features-gtunnels.txt','features/features-marsh.txt','features/premades.txt']

setup(
    version=version,
    data_files=[('.',dependencies),('features',features)],
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
os.chdir("dist")
for a,b, files in os.walk("."):
    for f in files:
        if f not in arc_exclude:
            target.write(os.path.join(a,f),os.path.join(a,f))
target.close()

for dirname, _, files in os.walk("."):
    for f in files:
        if ".pyc" in f:
            os.remove(os.path.join(dirname,f))