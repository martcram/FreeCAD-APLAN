# <img align="left" src="https://github.com/martcram/FreeCAD-APLAN/blob/main/freecad/aplan_workbench/resources/workbench_icon.svg" alt="APLAN workbench icon" width="53"> APLAN: Assembly PLANning workbench for FreeCAD
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v2.1-blue.svg)](https://www.gnu.org/licenses/lgpl-2.1)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-round)](https://github.com/martcram/FreeCAD-APLAN/pulls)

> :warning: **Work in progress:** the APLAN workbench is currently being extended to a C++/Python workbench under the ```cpp_py_wb``` branch.

## Description
This workbench is an attempt to introduce automatic assembly sequence planning (ASP) into FreeCAD. ASP involves determining (all) feasible sequences in which the different components of a product can be assembled successfully. Based on an assembly product's CAD model, feasible assembly sequences are composed by considering topological and geometrical constraints, and are represented as an AND/OR graph.

## Citation
This project started in the context of Ph.D. research into _intention-based human-robot collaborative assembly_, and was first mentioned in the following paper:
> M. Cramer, K. Kellens and E. Demeester, "Probabilistic Decision Model for Adaptive Task Planning in Human-Robot Collaborative Assembly Based on Designer and Operator Intents," in IEEE Robotics and Automation Letters, vol. 6, no. 4, pp. 7325-7332, Oct. 2021, doi: 10.1109/LRA.2021.3095513.

## Features
| Command | Description |
| ------- |:------------|
|<img align="left" src="https://github.com/martcram/FreeCAD-APLAN/blob/main/freecad/aplan_workbench/resources/transparency.svg" alt="Toggle transparency icon" width="45">|Toggles the transparency of the active part/assembly. This command can come in handy for visually inspecting the internal parts of a larger assembly.|
|<img align="left" src="https://github.com/martcram/FreeCAD-APLAN/blob/main/freecad/aplan_workbench/resources/connection.svg" alt="Generate connection graph icon" width="45">|Extracts the **topological constraints** between the different assembly components. Topological constraints are graphically represented by a connection graph: an undirected graph whose vertices depict the individual assembly components, and whose edges represent the (mechanical) connections between these component. The generated connection graph is stored in a directory named "APLAN" inside the active project folder.|
|<img align="left" src="https://github.com/martcram/FreeCAD-APLAN/blob/main/freecad/aplan_workbench/resources/obstruction.svg" alt="Generate obstruction graphs icon" width="45">|Extracts the **geometrical constraints** between the different assembly components. A (dis)assembly operation along a certain motion direction is geometrically constrained when a component’s movement is obstructed by other components. For this, a **collision detection** algorithm was developed using Open Cascade’s geometric kernel. Finally, these geometric constraints are graphically represented as obstruction graphs, which are constructed along the three positive Cartesian motion directions, and stored in a directory named "APLAN" inside the active project folder.|

## Setup
These instructions will help you get the APLAN workbench up and running on your local machine. 

1. Install FreeCAD: https://wiki.freecadweb.org/Manual:Installing.
2. The APLAN workbench isn't yet available in FreeCAD's addon manager. For the time being, a manual installation (see section below) is required.
3. Install the requisite Python packages:
```
$ cd ~/.FreeCAD/Mod/FreeCAD-APLAN/
$ pip3 install wheel
$ pip3 install .
```

### Installation
#### Manual installation on Linux distributions w/o using Git
* Within your home folder's (hidden) directory ``~/.FreeCAD``, create a new directory called "Mod" (if not already present):
```
$ mkdir -p ~/.FreeCAD/Mod
```
* Click on GitHub's "Code" button in the upper right corner and select "Download ZIP".
* Unpack the downloaded archive file and move it to the "Mod" directory:
```
$ sudo apt install unzip
$ unzip /path/to/FreeCAD-APLAN-<branch>.zip -d ~/.FreeCAD/Mod/
```
* After restarting FreeCAD, APLAN should now be available in the workbench selector.

#### Manual installation on Linux distributions w/ using Git
* Within your home folder's (hidden) directory ``~/.FreeCAD``, create a new directory called "Mod" (if not already present):
```
$ mkdir -p ~/.FreeCAD/Mod
```
* Click on GitHub's "Code" button in the upper right corner and clone this project into the "Mod" directory:
```
$ git clone <SSH or HTTPS> ~/.FreeCAD/Mod/
```
* After restarting FreeCAD, APLAN should now be available in the workbench selector.
* In addition, Git can be used to update to the latest version:
```
$ cd ~/.FreeCAD/Mod/FreeCAD-APLAN/
$ git pull
```

#### Manual installation on other operating systems
For the manual installation on Windows or MacOS, please refer to the [relevant page](https://wiki.freecadweb.org/How_to_install_additional_workbenches) of the official documentation.

### Tested with
* Ubuntu 20.04.2 LTS
* FreeCAD 0.19 (Daily)
* Python 3.9.1

## Usage
For more information regarding the usage and theoretical background of this workbench, please refer to the accompanying [wiki](https://github.com/martcram/FreeCAD-APLAN/wiki).

## Authors
See the list of [contributors](https://github.com/martcram/FreeCAD-APLAN/graphs/contributors) who participated in this project.

## License
This project is licensed under the LGPL-2.1 license - see the [LICENSE](https://github.com/martcram/FreeCAD-APLAN/blob/main/LICENSE) file for more details.

## Acknowledgments
* Workbench icon: <a href="https://www.flaticon.com/authors/monkik" title="monkik">monkik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> 
