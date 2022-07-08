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

__title__ = "FreeCAD APLAN OCCT obstruction detector"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

import FreeCAD
import Aplan
import aplansolvers.aplan_obstruction_detectors.base_obstruction_detector as base
import aplansolvers.aplan_obstruction_detectors.occt_view as occtView
from aplantools import aplanutils
try:
    import enum
    import itertools
    import MeshPart
    import random
    import typing
except ImportError as ie:
    print("Missing dependency! Please install the following Python module: {}".format(str(ie.name or "")))


class RefinementMethod(enum.Enum):
    None_ = ("None", "")
    BoundBox = ("BoundBox_Intersection", "Tooltip information about this refinement method")


class SolverMethod(enum.Enum):
    DistToShape   = ("BRepExtrema_DistShapeShape", "Tooltip information about this solver method")
    MeshInside    = ("BRepMesh_SolidClassifier",   "Tooltip information about this solver method")
    GeoDataInside = ("GeoData_SolidClassifier",    "Tooltip information about this solver method")
    Common        = ("Common",                     "Tooltip information about this solver method")
    Fuse          = ("Fuse",                       "Tooltip information about this solver method")


def create(doc, name="OCCT"):
    return aplanutils.createObject(doc, name, OCCT, occtView.VPOCCT)


class OCCT(base.IObstructionDetector):
    def __init__(self, obj):
        super(OCCT, self).__init__(obj)
        self.addProperties(obj)

    def addProperties(self, obj):
        if hasattr(obj, "Type"):
            obj.Type = self.__class__.__name__

        if not hasattr(obj, "RefinementMethod"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "RefinementMethod",
                "Obstruction detector",
                "Type of refinement method"
            )
            obj.RefinementMethod = [method.value[0] for method in RefinementMethod]

        if not hasattr(obj, "VariableStepSizeEnabled"):
            obj.addProperty(
                "App::PropertyBool",
                "VariableStepSizeEnabled",
                "Obstruction detector",
                "..."
            )
            obj.VariableStepSizeEnabled = True

        if not hasattr(obj, "StepSizeCoefficient"):
            obj.addProperty(
                "App::PropertyFloat",
                "StepSizeCoefficient",
                "Obstruction detector",
                "..."
            )
            obj.StepSizeCoefficient = 0.1

        if not hasattr(obj, "MinStepSize"):
            obj.addProperty(
                "App::PropertyFloat",
                "MinStepSize",
                "Obstruction detector",
                "..."
            )
            obj.MinStepSize = 1.0
        
        if not hasattr(obj, "FixedStepSize"):
            obj.addProperty(
                "App::PropertyFloat",
                "FixedStepSize",
                "Obstruction detector",
                "..."
            )
            obj.FixedStepSize = 1.0

        if not hasattr(obj, "SolverMethod"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "SolverMethod",
                "Obstruction detector",
                "Type of solver method"
            )
            obj.SolverMethod = [method.value[0] for method in SolverMethod]
               
        if not hasattr(obj, "MinDistance"):
            obj.addProperty(
                "App::PropertyFloat",
                "MinDistance",
                "Obstruction detector",
                "..."
            )
            obj.MinDistance = 0.00001
        
        if not hasattr(obj, "OverlapTolerance"):
            obj.addProperty(
                "App::PropertyFloat",
                "OverlapTolerance",
                "Obstruction detector",
                "..."
            )
            obj.OverlapTolerance = 0.00001
        
        if not hasattr(obj, "ClassificationTolerance"):
            obj.addProperty(
                "App::PropertyFloat",
                "ClassificationTolerance",
                "Obstruction detector",
                "..."
            )
            obj.ClassificationTolerance = 0.00001
        
        if not hasattr(obj, "VolumeTolerance"):
            obj.addProperty(
                "App::PropertyFloat",
                "VolumeTolerance",
                "Obstruction detector",
                "..."
            )
            obj.VolumeTolerance = 0.00001
        
        if not hasattr(obj, "SampleCoefficient"):
            obj.addProperty(
                "App::PropertyFloat",
                "SampleCoefficient",
                "Obstruction detector",
                "..."
            )
            obj.SampleCoefficient = 0.01
        
        if not hasattr(obj, "MotionDirections"):
            obj.addProperty(
                "App::PropertyStringList",
                "MotionDirections",
                "Obstruction detector",
                "..."
            )
            obj.MotionDirections = [str(motionDirection.name) 
                                    for motionDirection in base.CartesianMotionDirection]

        if not hasattr(obj, "MultiprocessingEnabled"):
            obj.addProperty(
                "App::PropertyBool",
                "MultiprocessingEnabled",
                "Obstruction detector",
                "..."
            )
            obj.MultiprocessingEnabled = False
        
        if not hasattr(obj, "LinearDeflection"):
            obj.addProperty(
                "App::PropertyFloat",
                "LinearDeflection",
                "Obstruction detector",
                "..."
            )
            obj.LinearDeflection = 0.1


class OCCTSolver:
    def __init__(self, components: typing.List, motionDirections: typing.Set[base.CartesianMotionDirection], linearDeflection: float = 0.1) -> None:
        self._isRunning: bool = True
        self._linearDeflection: float = linearDeflection
        self.setComponents(components)
        self._nonRedundantMotionDirs: typing.Set[base.CartesianMotionDirection] = {base.CartesianMotionDirection(abs(motionDir_.value)) 
                                                                                   for motionDir_ in motionDirections}
        self._partPointsMeshDict: typing.Dict = {}
        self._partPointsSampleDict: typing.Dict = {}

    def setComponents(self, components: typing.List) -> None:
        if not FreeCAD.GuiUp:
            # In order for TopoShapePy::proximity to work, every shape's faces need to be tessellated. 
            # This is not done by default when FreeCAD's GUI is not running. 
            # Source: https://forum.freecadweb.org/viewtopic.php?t=22857
            for component in components:
                for face in component.Shape.Faces:
                    face.tessellate(self._linearDeflection)
        self._componentsDict = {component.Label: component for component in components}

    def refine(self, method: RefinementMethod, configParam: typing.Dict) -> typing.Dict:       
        overallBoundbox = FreeCAD.BoundBox()
        for component in self._componentsDict.values():
            overallBoundbox.add(component.Shape.BoundBox)
        if not self._isRunning:
                return {}
        componentsIntervalDict: typing.Dict = {}
        motionDirection_: base.CartesianMotionDirection
        for motionDirection_ in self._nonRedundantMotionDirs:
            if not self._isRunning:
                return {}
            componentsIntervalDict[motionDirection_.name] = {}
            for target in self._componentsDict.values():
                if not self._isRunning:
                    return {}
                intersectionComponents: typing.List[typing.List] = []
                intervals: typing.List[typing.List[float]] = []
                if method == RefinementMethod.None_:
                    if motionDirection_ == base.CartesianMotionDirection.POS_X:
                        intervals.append([target.Shape.BoundBox.XMin, overallBoundbox.XMax])
                    elif motionDirection_ == base.CartesianMotionDirection.POS_Y:
                        intervals.append([target.Shape.BoundBox.YMin, overallBoundbox.YMax])
                    elif motionDirection_ == base.CartesianMotionDirection.POS_Z:
                        intervals.append([target.Shape.BoundBox.ZMin, overallBoundbox.ZMax])
                    intersectionComponents = [[comp for comp in self._componentsDict.values() if comp != target]]
                elif method == RefinementMethod.BoundBox:
                    intersectionComponents, intervals = self.__findPotentialObstacles(target, {component for component in self._componentsDict.values() 
                                                                                               if component.Label != target.Label}, 
                                                                                      motionDirection_, overallBoundbox)
                componentsIntervalDict[motionDirection_.name][target.Label] = [intersectionComponents, intervals]
        return componentsIntervalDict

    def solve(self, method: SolverMethod, configParam: typing.Dict, configParamGeneral: typing.Dict, **kwargs) -> typing.Dict[base.CartesianMotionDirection, typing.Set[typing.Tuple[str, str]]]:
        movePart: typing.Callable = kwargs.get("movePart", self.movePart)
        setPartPlacement: typing.Callable = kwargs.get("setPartPlacement", self.setPartPlacement)
        
        componentsIntervalDict: typing.Dict = kwargs.get("componentsIntervalDict", self.refine(RefinementMethod.None_, {}))
        geomConstraints: typing.Dict[base.CartesianMotionDirection, typing.Set[typing.Tuple[str, str]]] = {motionDir: set() for motionDir in self._nonRedundantMotionDirs}

        motionDirection_: base.CartesianMotionDirection
        for motionDirection_ in self._nonRedundantMotionDirs:
            if not self._isRunning:
                return {}
            for target in self._componentsDict.values():
                if not self._isRunning:
                    return {}
                
                targetStartPosition = target.Placement

                difference: float = 0.0
                if motionDirection_ == base.CartesianMotionDirection.POS_X:
                    difference = target.Placement.Base[0]-target.Shape.BoundBox.XMin
                elif motionDirection_ == base.CartesianMotionDirection.POS_Y:
                    difference = target.Placement.Base[1]-target.Shape.BoundBox.YMin
                elif motionDirection_ == base.CartesianMotionDirection.POS_Z:
                    difference = target.Placement.Base[2]-target.Shape.BoundBox.ZMin
                
                collidingObjects: typing.Set = set()
                index: int
                interval: typing.List[float]
                for index, interval in enumerate(componentsIntervalDict[motionDirection_.name][target.Label][1]):
                    if not self._isRunning:
                        return {}

                    stepSize: float = float(configParamGeneral["fixedStepSize"])
                    if bool(configParamGeneral["variableStepSizeEnabled"]):
                        stepSize = max(((interval[1]-interval[0])*float(configParamGeneral["stepSizeCoefficient"])), float(configParamGeneral["minStepSize"]))

                    if motionDirection_ == base.CartesianMotionDirection.POS_X:
                        baseVector_ = FreeCAD.Vector(interval[0]+difference, targetStartPosition.Base[1], targetStartPosition.Base[2])
                    elif motionDirection_ == base.CartesianMotionDirection.POS_Y:
                        baseVector_ = FreeCAD.Vector(targetStartPosition.Base[0], interval[0]+difference, targetStartPosition.Base[2])
                    elif motionDirection_ == base.CartesianMotionDirection.POS_Z:
                        baseVector_ = FreeCAD.Vector(targetStartPosition.Base[0], targetStartPosition.Base[1], interval[0]+difference)
                    setPartPlacement(target, baseVector_, targetStartPosition.Rotation)

                    potentialObstacles: typing.List = componentsIntervalDict[motionDirection_.name][target.Label][0][index]
                    targetPosition = interval[0]
                    while targetPosition < interval[1]:
                        if not self._isRunning:
                            return {}

                        if sum([True for obj in potentialObstacles if obj in collidingObjects]) == len(potentialObstacles):
                            break

                        if motionDirection_ == base.CartesianMotionDirection.POS_X:
                            vector_ = FreeCAD.Vector(stepSize, 0.0, 0.0)
                        elif motionDirection_ == base.CartesianMotionDirection.POS_Y:
                            vector_ = FreeCAD.Vector(0.0, stepSize, 0.0)
                        elif motionDirection_ == base.CartesianMotionDirection.POS_Z:
                            vector_ = FreeCAD.Vector(0.0, 0.0, stepSize)
                        movePart(target, vector_)

                        obstacles: typing.Set = {obst for obst in potentialObstacles if obst not in collidingObjects}
                        collidingObjects = self.__detectCollisions(target, obstacles, collidingObjects, method, configParam)

                        if not self._isRunning:
                            return {}

                        if motionDirection_ == base.CartesianMotionDirection.POS_X:
                            targetPosition = target.Shape.BoundBox.XMin
                        elif motionDirection_ == base.CartesianMotionDirection.POS_Y:
                            targetPosition = target.Shape.BoundBox.YMin
                        elif motionDirection_ == base.CartesianMotionDirection.POS_Z:
                            targetPosition = target.Shape.BoundBox.ZMin

                setPartPlacement(target, targetStartPosition.Base, targetStartPosition.Rotation)

                geomConstraints[motionDirection_] = geomConstraints[motionDirection_].union({(target.Label, obj.Label) for obj in collidingObjects})
        return geomConstraints

    def movePart(self, part, displacementVector) -> None:
        part.Placement.move(displacementVector)
    
    def setPartPlacement(self, part, baseVector, rotationVector) -> None:
        part.Placement = FreeCAD.Placement(baseVector, rotationVector)

    def stop(self) -> None:
        self._isRunning = False

    def __detectCollisions(self, target, potentialObstacles: typing.Set, collidingObjects: typing.Set, solverMethod: SolverMethod, configParams: typing.Dict) -> typing.Set:
        # av = target.Shape.BoundBox
        for obl in potentialObstacles:
            if not self._isRunning:
                return set()
            # ov = obl.Shape.BoundBox
            # if av.intersect(ov):
            #     intersection = av.intersected(ov)
            #     if intersection.XLength > 0.01 or intersection.YLength > 0.01 or intersection.ZLength > 0.01:

                    # if len(target.Shape.Vertexes) > len(obl.Shape.Vertexes):
                    #     shape_big = target
                    #     shape_small = obl
                    # else:
                    #     shape_small = target
                    #     shape_big = obl
                    # inside_pt_found = False
                    # for vertex in shape_small.Shape.Vertexes:
                    #     if intersection.isInside(vertex.Point):
                    #         if shape_big.Shape.isInside(vertex.Point, 10**-6, False):
                    #             inside_pt_found = True
                    #             collidingObjects.add(obl)
                    #             break

                    # if not inside_pt_found:

            overlappedSubShapes0, overlappedSubShapes1 = target.Shape.proximity(obl.Shape, float(configParams["overlapTolerance"]))
            if len(overlappedSubShapes0) > 0 or len(overlappedSubShapes1) > 0:
                if solverMethod == SolverMethod.DistToShape:
                    dist, pointPairs, _ = target.Shape.distToShape(obl.Shape)
                    if dist < float(configParams["minDistance"]):
                        for pointPair in pointPairs:
                            if not self._isRunning:
                                return set()
                            if target.Shape.isInside(pointPair[1], float(configParams["classificationTolerance"]), False) or obl.Shape.isInside(pointPair[0], float(configParams["classificationTolerance"]), False):
                                collidingObjects.add(obl)
                                break
                elif solverMethod == SolverMethod.MeshInside:
                    boundBox = obl.Shape.BoundBox
                    maxLength: float = min(boundBox.XLength, boundBox.YLength, boundBox.ZLength) * float(configParams["sampleCoefficient"])
                    if obl.Label not in self._partPointsMeshDict.keys():
                        self._partPointsMeshDict[obl.Label] = MeshPart.meshFromShape(Shape=obl.Shape, MaxLength=maxLength).Points
                    meshPoints: typing.List = self._partPointsMeshDict[obl.Label]
                    for p in random.sample(meshPoints, len(meshPoints)):
                        if not self._isRunning:
                            return set()
                        if target.Shape.isInside(FreeCAD.Vector(p.x, p.y, p.z), float(configParams["classificationTolerance"]), False):
                            collidingObjects.add(obl)
                            break
                elif solverMethod == SolverMethod.GeoDataInside:
                    boundBox = obl.Shape.BoundBox
                    distance: float = min(boundBox.XLength, boundBox.YLength, boundBox.ZLength) * float(configParams["sampleCoefficient"])
                    if obl.Label not in self._partPointsSampleDict.keys():
                        self._partPointsSampleDict[obl.Label] = Aplan.pointSampleShape(obl.Label, distance)
                    samplePoints: typing.List = self._partPointsSampleDict[obl.Label]
                    point: typing.Tuple[float, float, float]
                    for point in random.sample(samplePoints, len(samplePoints)):
                        if not self._isRunning:
                            return set()
                        if target.Shape.isInside(FreeCAD.Vector(*point), float(configParams["classificationTolerance"]), False):
                            collidingObjects.add(obl)
                            break
                elif solverMethod == SolverMethod.Common:
                    if target.Shape.common(obl.Shape).Volume > float(configParams["volumeTolerance"]):
                        collidingObjects.add(obl)
                elif solverMethod == SolverMethod.Fuse:
                    if target.Shape.fuse(obl.Shape).Volume < (target.Shape.Volume + obl.Shape.Volume - float(configParams["volumeTolerance"])):
                        collidingObjects.add(obl)

        return collidingObjects

    def __findPotentialObstacles(self, target, components: typing.Set, motionDirection: base.CartesianMotionDirection, overallBoundBox) -> typing.Tuple[typing.List[typing.List], typing.List[typing.List[float]]]:
        targetBoundBox = target.Shape.BoundBox
        targetBoundary: float = 0.0
        targetSize: float = 0.0

        if motionDirection == base.CartesianMotionDirection.POS_X:
            elongatedBoundBox = FreeCAD.BoundBox(targetBoundBox.XMin, targetBoundBox.YMin, targetBoundBox.ZMin, 
                                                 overallBoundBox.XMax, targetBoundBox.YMax, targetBoundBox.ZMax)
            targetBoundary = targetBoundBox.XMin
            targetSize = targetBoundBox.XLength
        elif motionDirection == base.CartesianMotionDirection.POS_Y:
            elongatedBoundBox = FreeCAD.BoundBox(targetBoundBox.XMin, targetBoundBox.YMin, targetBoundBox.ZMin, 
                                                 targetBoundBox.XMax, overallBoundBox.YMax, targetBoundBox.ZMax)
            targetBoundary = targetBoundBox.YMin
            targetSize = targetBoundBox.YLength
        elif motionDirection == base.CartesianMotionDirection.POS_Z:
            elongatedBoundBox = FreeCAD.BoundBox(targetBoundBox.XMin, targetBoundBox.YMin, targetBoundBox.ZMin, 
                                                 targetBoundBox.XMax, targetBoundBox.YMax, overallBoundBox.ZMax)
            targetBoundary = targetBoundBox.ZMin
            targetSize = targetBoundBox.ZLength          

        potentialObstacles: typing.List = []
        intersections: typing.List[typing.List[float]] = []
        for comp in components:
            if not self._isRunning:
                return [], []
            if elongatedBoundBox.intersect(comp.Shape.BoundBox):
                intersection = elongatedBoundBox.intersected(comp.Shape.BoundBox)
                if intersection.XLength > 0.01 and intersection.YLength > 0.01 and intersection.ZLength > 0.01:
                    potentialObstacles.append(comp)
                    if motionDirection == base.CartesianMotionDirection.POS_X:
                        intersections.append([intersection.XMin, intersection.XMax])
                    elif motionDirection == base.CartesianMotionDirection.POS_Y:
                        intersections.append([intersection.YMin, intersection.YMax])
                    elif motionDirection == base.CartesianMotionDirection.POS_Z:
                        intersections.append([intersection.ZMin, intersection.ZMax])

        intersectionComponents: typing.List[typing.List] = []
        intervals: typing.List[typing.List[float]] = []
        if potentialObstacles and intersections:
            if not self._isRunning:
                return [], []
            sortedIntersections: typing.Tuple[typing.List[float]]
            sortedObstacles: typing.Tuple[typing.List]
            sortedIntersections, sortedObstacles = zip(*sorted(zip(intersections, potentialObstacles)))
            if not self._isRunning:
                return [], []
            shiftedIntersections: typing.List[typing.List[float]] = [[max(targetBoundary, (intersection[0]-targetSize)), 
                                                                      intersection[1]] for intersection in sortedIntersections]
            intervalBoundaries: typing.List[float] = sorted(set(itertools.chain.from_iterable(shiftedIntersections)))
            intervals = [[first, second] for first, second in zip(intervalBoundaries, intervalBoundaries[1:])]
            if not self._isRunning:
                return [], []
            intersectionComponents = [[sortedObstacles[index] for index, intersection in enumerate(shiftedIntersections) 
                                       if interval[0] < intersection[1] and intersection[0] < interval[1]] 
                                       for interval in intervals]
            intersectionComponents, intervals = zip(*[(obstacles, interval) for obstacles, interval in zip(intersectionComponents, intervals) 
                                                      if obstacles])

        return list(intersectionComponents), list(intervals)
