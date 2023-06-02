<div id="top"></div>

[![PRs][prs-shield]][prs-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/martcram/FreeCAD-APLAN/blob/main/Gui/Resources/icons/APLAN_Workbench.svg">
    <img src="https://github.com/martcram/FreeCAD-APLAN/blob/main/Gui/Resources/icons/APLAN_Workbench.svg" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">APLAN: Assembly PLANning workbench for FreeCAD</h3>
  <p align="center">
    <a href="https://github.com/martcram/FreeCAD-APLAN/issues">Report Bug</a>
    ·
    <a href="https://github.com/martcram/FreeCAD-APLAN/issues">Request Feature</a>
    <br />
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About the project</a>
      <ul>
        <li><a href="#citation">Citation</a></li>
        <li><a href="#built-with">Built with</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting started</a>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About the project
:warning: **Work in progress** :warning:
<!--[![Product Name Screen Shot][product-screenshot]](https://example.com)-->
This workbench is an attempt to introduce automatic assembly sequence planning (ASP) into FreeCAD. ASP involves determining (all) feasible sequences in which the different components of a product can be assembled successfully. Based on an assembly product's CAD model, feasible assembly sequences are composed by considering topological and geometrical constraints, and are represented as an AND/OR graph.

### Citation
This project started in the context of Ph.D. research into _intention-based human-robot collaborative assembly_, and was first mentioned in the following paper:
> M. Cramer, K. Kellens and E. Demeester, "Probabilistic Decision Model for Adaptive Task Planning in Human-Robot Collaborative Assembly Based on Designer and Operator Intents," in IEEE Robotics and Automation Letters, vol. 6, no. 4, pp. 7325-7332, Oct. 2021, doi: 10.1109/LRA.2021.3095513.

### Built with
* FreeCAD version info:
```
OS: Ubuntu 22.04 LTS (ubuntu:GNOME/ubuntu)
Word size of FreeCAD: 64-bit
Version: 0.20.29177 (Git)
Build type: Release
Branch: (HEAD detached at 0.20)
Hash: 68e337670e227889217652ddac593c93b5e8dc94
Python 3.10.4, Qt 5.15.3, Coin 4.0.0, Vtk 7.1.1, OCC 7.5.1
Locale: English/United States (en_US)
```

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting started
These instructions will help you get the APLAN workbench up and running on your local machine. 

1. Copy the latest version of FreeCAD's [source code](https://github.com/FreeCAD/FreeCAD):
```
$ git clone https://github.com/FreeCAD/FreeCAD.git freecad/freecad-source
```
2. Copy the source code of the APLAN workbench into the Mod folder:
```
$ git clone https://github.com/martcram/FreeCAD-APLAN.git freecad/freecad-source/src/Mod/Aplan
```
... or include the project as a submodule for development purposes:
```
$ cd freecad/freecad-source
$ git submodule add https://github.com/martcram/FreeCAD-APLAN.git src/Mod/Aplan
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

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this workbench better, please fork the repo and create a pull request. You can also simply open an issue with the tag "Feature".
Don't forget to give the project a star! Thank you!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazingFeature`)
3. Commit your Changes (`git commit -m 'add some amazingFeature'`)
4. Push to the Branch (`git push origin feature/amazingFeature`)
5. Open a Pull Request

Finally, have a look at the list of [contributors](https://github.com/martcram/FreeCAD-APLAN/graphs/contributors) who participated in this project.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- LICENSE -->
## License
This project is distributed under the LGPL-2.1 License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
* [FreeCAD](https://www.freecadweb.org/) and its [community](https://forum.freecadweb.org/)
* [KU Leuven](https://iiw.kuleuven.be/english/diepenbeek) @ Diepenbeek Campus
* Automation, Computer vision and Robotics ([ACRO](https://iiw.kuleuven.be/onderzoek/acro)) research unit
* Research Foundation - Flanders ([FWO](https://www.fwo.be/en/))
* FlandersMake@KU Leuven
* Workbench icon: <a href="https://www.flaticon.com/authors/monkik" title="monkik">monkik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
[prs-shield]: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge
[prs-url]: https://github.com/martcram/FreeCAD-APLAN/pulls
[stars-shield]: https://img.shields.io/github/stars/martcram/FreeCAD-APLAN.svg?style=for-the-badge
[stars-url]: https://github.com/martcram/FreeCAD-APLAN/stargazers
[issues-shield]: https://img.shields.io/github/issues/martcram/FreeCAD-APLAN.svg?style=for-the-badge
[issues-url]: https://github.com/martcram/FreeCAD-APLAN/issues
[license-shield]: https://img.shields.io/github/license/martcram/FreeCAD-APLAN.svg?style=for-the-badge
[license-url]: https://github.com/martcram/FreeCAD-APLAN/blob/master/LICENSE.txt
