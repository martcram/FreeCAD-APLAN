[![PRs][prs-shield]][prs-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

# <img align="left" src="https://github.com/martcram/FreeCAD-APLAN/blob/main/Gui/Resources/icons/APLAN_Workbench.svg" alt="APLAN workbench icon" width="53"> APLAN: Assembly PLANning workbench for FreeCAD

> :warning: **Work in progress**

## Description
This workbench is an attempt to introduce automatic assembly sequence planning (ASP) into FreeCAD. ASP involves determining (all) feasible sequences in which the different components of a product can be assembled successfully. Based on an assembly product's CAD model, feasible assembly sequences are composed by considering topological and geometrical constraints, and are represented as an AND/OR graph.

## Citation
This project started in the context of Ph.D. research into _intention-based human-robot collaborative assembly_, and was first mentioned in the following paper:
> M. Cramer, K. Kellens and E. Demeester, "Probabilistic Decision Model for Adaptive Task Planning in Human-Robot Collaborative Assembly Based on Designer and Operator Intents," in IEEE Robotics and Automation Letters, vol. 6, no. 4, pp. 7325-7332, Oct. 2021, doi: 10.1109/LRA.2021.3095513.

## Setup
These instructions will help you get the APLAN workbench up and running on your local machine. 

1. Copy the latest version of FreeCAD's source code:
```
$ git clone https://github.com/FreeCAD/FreeCAD.git freecad/freecad-source
```
2. Copy the source code of the APLAN workbench into the Mod folder:
```
$ git clone https://github.com/martcram/FreeCAD-APLAN.git freecad/freecad-source/src/Mod/Aplan
```
3. Create a CMake variable in the file ```freecad-source/cMake/FreeCAD_Helpers/InitializeFreeCADBuildOptions.cmake``` to provide the user with the option to compile this workbench:
```
...
option(BUILD_APLAN "Build the FreeCAD APLAN module" ON)
...
```
4. Include the subdirectory of the APLAN workbench in the CMake build by adding the following lines to the file ```freecad-source/src/Mod/CMakeLists.txt```:
```
...
if(BUILD_APLAN)
    add_subdirectory(Aplan)
endif(BUILD_APLAN)
...
```
5. Follow the succeeding [instructions](https://wiki.freecadweb.org/Compiling) for compiling FreeCAD on your specific OS using the official documentation. 
Note that the first step of acquiring FreeCAD's source code can be disregarded since this was already addressed by this README file. 

## Usage
For more information regarding the usage and theoretical background of this workbench, please refer to the accompanying [wiki](https://github.com/martcram/FreeCAD-APLAN/wiki).

## Authors
See the list of [contributors](https://github.com/martcram/FreeCAD-APLAN/graphs/contributors) who participated in this project.

## License
This project is licensed under the LGPL-2.1 license - see the [LICENSE](https://github.com/martcram/FreeCAD-APLAN/blob/main/LICENSE) file for more details.

## Acknowledgments
* [FreeCAD](https://www.freecadweb.org/) and its [community](https://forum.freecadweb.org/)
* [KU Leuven](https://iiw.kuleuven.be/english/diepenbeek) @ Diepenbeek Campus
* Automation, Computer vision and Robotics ([ACRO](https://iiw.kuleuven.be/onderzoek/acro)) research unit
* Research Foundation - Flanders ([FWO](https://www.fwo.be/en/))
* Workbench icon: <a href="https://www.flaticon.com/authors/monkik" title="monkik">monkik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>


<!-- MARKDOWN LINKS & IMAGES -->
[prs-shield]: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge
[prs-url]: https://github.com/martcram/FreeCAD-APLAN/pulls
[stars-shield]: https://img.shields.io/github/stars/martcram/FreeCAD-APLAN.svg?style=for-the-badge
[stars-url]: https://github.com/martcram/FreeCAD-APLAN/stargazers
[issues-shield]: https://img.shields.io/github/issues/martcram/FreeCAD-APLAN.svg?style=for-the-badge
[issues-url]: https://github.com/martcram/FreeCAD-APLAN/issues
[license-shield]: https://img.shields.io/github/license/martcram/FreeCAD-APLAN.svg?style=for-the-badge
[license-url]: https://github.com/martcram/FreeCAD-APLAN/blob/master/LICENSE.txt
