# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2022 Martijn Cramer <martijn.cramer@outlook.com>        *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "Methods to divide OCCT's obstruction detection among multiple processes"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

try:
    import argparse
    from concurrent.futures import ProcessPoolExecutor
    import itertools
    import json
    import os
    import sys
    import time
    import typing
except ImportError as ie:
    print("Missing dependency! Please install the following Python module: {}".format(str(ie.name or "")))

try:
    import FreeCAD
except ModuleNotFoundError as me:
    FREECAD_LIBDIR: typing.Optional[str]
    if FREECAD_LIBDIR := os.getenv("FREECAD_LIBDIR"):
        sys.path.append(FREECAD_LIBDIR)
        import FreeCAD
        import aplansolvers.aplan_obstruction_detectors.base_obstruction_detector as base
        import aplansolvers.aplan_obstruction_detectors.occt as occt
    else:
        print("Missing environment variable!",
              "Please add FREECAD_LIBDIR (i.e. the path of your FreeCAD's library directory) to your machine's environment variables.")


def multiprocess(filePath: str,
                 componentLabels: typing.List[str],
                 motionDirection: base.CartesianMotionDirection,
                 linearDeflection: float,
                 refinementMethod: occt.RefinementMethod, 
                 configParamRefinement: typing.Dict,
                 solverMethod: occt.SolverMethod, 
                 configParamSolver: typing.Dict,
                 configParamSolverGeneral: typing.Dict) -> typing.Tuple[typing.Set[typing.Tuple[str, str]], float]:
    doc = FreeCAD.openDocument(filePath, hidden=True)
    components: typing.Set[typing.Any] = {doc.getObjectsByLabel(label)[0] for label in componentLabels}
    solver: occt.OCCTSolver = occt.OCCTSolver(components, [motionDirection], linearDeflection)
    time0: float = time.perf_counter()
    intervalObstructionsDict: typing.Dict = solver.refine(refinementMethod, 
                                                          configParamRefinement)
    geometricalConstraints: typing.Dict[base.CartesianMotionDirection, typing.Set[typing.Tuple[str, str]]] = solver.solve(solverMethod, 
                                                                                                                          configParamSolver, 
                                                                                                                          configParamSolverGeneral,
                                                                                                                          intervalObstructionsDict=intervalObstructionsDict)
    time1: float = time.perf_counter()
    return geometricalConstraints[motionDirection], time1-time0


def main(arguments: argparse.Namespace) -> None:
    filePath: str = arguments.file_path
    componentLabels: typing.List[str] = eval(arguments.component_labels)
    motionDirections: typing.Set[base.CartesianMotionDirection] = set(map(base.CartesianMotionDirection, eval(arguments.motion_directions)))
    nonRedundantMotionDirs: typing.Set[base.CartesianMotionDirection] = set()
    motionDirectionValues: typing.Set[int] = {motionDir.value for motionDir in motionDirections}
    motionDirValue: int
    for motionDirValue in motionDirectionValues:
        if -motionDirValue in motionDirectionValues:
            nonRedundantMotionDirs.add(base.CartesianMotionDirection(abs(motionDirValue)))
        else:
            nonRedundantMotionDirs.add(base.CartesianMotionDirection(motionDirValue))
    linearDeflection: float = float(arguments.linear_deflection)

    try:
        refinementMethod: occt.RefinementMethod = next(r for r in occt.RefinementMethod if r.name == arguments.refinement_method)
    except StopIteration:
        refinementMethod = occt.RefinementMethod.None_
        print("Unknown refiner! Could not find the {} refinement method. Defaulting to {}".format(arguments.refinement_method, refinementMethod))
        return None
    configParamRefinement: typing.Dict = json.loads(arguments.config_param_refinement)

    try:
        solverMethod: occt.SolverMethod = next(s for s in occt.SolverMethod if s.name == arguments.solver_method)
    except StopIteration:
        print("Unknown solver! Could not find the {} solver method. Aborting ...".format(arguments.solver_method))
        return None
    configParamSolver: typing.Dict = json.loads(arguments.config_param_solver)
    configParamSolverGeneral: typing.Dict = json.loads(arguments.config_param_solver_general)

    geomConstraintDict: typing.Dict[int, typing.Tuple[typing.Set[typing.Tuple[str, str]], float]] = {motionDir.value: (set(), 0.0) for motionDir in motionDirections}
    noMotionDirections: int = len(motionDirections)
    with ProcessPoolExecutor(max_workers = noMotionDirections) as executor:
        for motionDirection, output in zip(nonRedundantMotionDirs, executor.map(multiprocess,
                                                                                itertools.repeat(filePath,                 noMotionDirections),
                                                                                itertools.repeat(componentLabels,          noMotionDirections),
                                                                                nonRedundantMotionDirs,
                                                                                itertools.repeat(linearDeflection,         noMotionDirections),
                                                                                itertools.repeat(refinementMethod,         noMotionDirections),
                                                                                itertools.repeat(configParamRefinement,    noMotionDirections),
                                                                                itertools.repeat(solverMethod,             noMotionDirections),
                                                                                itertools.repeat(configParamSolver,        noMotionDirections),
                                                                                itertools.repeat(configParamSolverGeneral, noMotionDirections))):
            geomConstraintDict[motionDirection.value] = output 

    motionDirection_: base.CartesianMotionDirection
    for motionDirection_ in motionDirections.difference(nonRedundantMotionDirs):
        oppositeMotionDirection: base.CartesianMotionDirection = base.CartesianMotionDirection(-motionDirection_.value)
        geomConstraintDict[motionDirection_.value] = ({constraint[::-1] for constraint in geomConstraintDict[oppositeMotionDirection.value][0]}, 0.0)
    
    print(geomConstraintDict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path",                   type=str)
    parser.add_argument("--component_labels",            type=str)
    parser.add_argument("--motion_directions",           type=str)
    parser.add_argument("--linear_deflection",           type=str, nargs='?', default="0.1")
    parser.add_argument("--refinement_method",           type=str, nargs='?', default=occt.RefinementMethod.None_.name)
    parser.add_argument("--config_param_refinement",     type=str, nargs='?', default="{}")
    parser.add_argument("--solver_method",               type=str)
    parser.add_argument("--config_param_solver",         type=str)
    parser.add_argument("--config_param_solver_general", type=str)
    args: argparse.Namespace
    args, _ = parser.parse_known_args()
    main(args)
