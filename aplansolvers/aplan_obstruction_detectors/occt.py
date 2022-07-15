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


# **** START: Default values ****

DEF_VAR_STEP_SIZE_ENABLED: bool  = True
DEF_STEP_SIZE_COEFF:       float = 0.1
DEF_MIN_STEP_SIZE:         float = 1.0
DEF_FIXED_STEP_SIZE:       float = 1.0
DEF_MIN_DIST:              float = 1e-5
DEF_OVERLAP_TOL:           float = 1e-5
DEF_CLASSIF_TOL:           float = 1e-5
DEF_VOLUME_TOL:            float = 1e-5
DEF_SAMPLE_COEFF:          float = 1e-2
DEF_LIN_DEFLECT:           float = 0.1

# **** END: Default values ****


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
            obj.VariableStepSizeEnabled = DEF_VAR_STEP_SIZE_ENABLED

        if not hasattr(obj, "StepSizeCoefficient"):
            obj.addProperty(
                "App::PropertyFloat",
                "StepSizeCoefficient",
                "Obstruction detector",
                "..."
            )
            obj.StepSizeCoefficient = DEF_STEP_SIZE_COEFF

        if not hasattr(obj, "MinStepSize"):
            obj.addProperty(
                "App::PropertyFloat",
                "MinStepSize",
                "Obstruction detector",
                "..."
            )
            obj.MinStepSize = DEF_MIN_STEP_SIZE
        
        if not hasattr(obj, "FixedStepSize"):
            obj.addProperty(
                "App::PropertyFloat",
                "FixedStepSize",
                "Obstruction detector",
                "..."
            )
            obj.FixedStepSize = DEF_FIXED_STEP_SIZE

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
            obj.MinDistance = DEF_MIN_DIST
        
        if not hasattr(obj, "OverlapTolerance"):
            obj.addProperty(
                "App::PropertyFloat",
                "OverlapTolerance",
                "Obstruction detector",
                "..."
            )
            obj.OverlapTolerance = DEF_OVERLAP_TOL
        
        if not hasattr(obj, "ClassificationTolerance"):
            obj.addProperty(
                "App::PropertyFloat",
                "ClassificationTolerance",
                "Obstruction detector",
                "..."
            )
            obj.ClassificationTolerance = DEF_CLASSIF_TOL
        
        if not hasattr(obj, "VolumeTolerance"):
            obj.addProperty(
                "App::PropertyFloat",
                "VolumeTolerance",
                "Obstruction detector",
                "..."
            )
            obj.VolumeTolerance = DEF_VOLUME_TOL
        
        if not hasattr(obj, "SampleCoefficient"):
            obj.addProperty(
                "App::PropertyFloat",
                "SampleCoefficient",
                "Obstruction detector",
                "..."
            )
            obj.SampleCoefficient = DEF_SAMPLE_COEFF
        
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
            obj.LinearDeflection = DEF_LIN_DEFLECT


class OCCTRefiner:
    def __init__(self, components: typing.Iterable) -> None:
        self._isRunning: bool = False
        self._components: typing.Set = set(components)
        self._overallBoundBox = self.__overallBoundbox(self._components)

    # ********************* START: Getters & Setters *********************

    @property
    def components(self):
        return self._components

    @components.setter
    def components(self, components: typing.Iterable) -> None:
        for component in components:
            self.addComponent(component)

    def addComponent(self, component) -> None:
        if component not in self._components:
            self._components.add(component)
            self._overallBoundBox.add(component.Shape.BoundBox)

    def removeComponent(self, component) -> None:
        if component in self._components:
            self._components.remove(component)
            self._overallBoundBox = self.__overallBoundbox(component.Shape.BoundBox)

    @property
    def isRunning(self):
        return self._isRunning

    # ********************* END: Getters & Setters *********************

    def __overallBoundbox(self, components: typing.Iterable):
        overallBoundbox = FreeCAD.BoundBox()
        for component in components:
            overallBoundbox.add(component.Shape.BoundBox)
        return overallBoundbox

    def __potentialObstructionIntervals(self, target, 
                                              components: typing.Iterable, 
                                              motionDirection: base.CartesianMotionDirection) -> typing.List[typing.Tuple[typing.Tuple[float, float], 
                                                                                                                          typing.Set[typing.Any]]]:
        targetBoundBox = target.Shape.BoundBox
        targetBoundary: float = 0.0
        targetSize: float = 0.0

        if motionDirection == base.CartesianMotionDirection.POS_X:
            elongatedBoundBox = FreeCAD.BoundBox(targetBoundBox.XMin, targetBoundBox.YMin, targetBoundBox.ZMin, 
                                                 self._overallBoundBox.XMax, targetBoundBox.YMax, targetBoundBox.ZMax)
            targetBoundary = targetBoundBox.XMin
            targetSize = targetBoundBox.XLength
        elif motionDirection == base.CartesianMotionDirection.POS_Y:
            elongatedBoundBox = FreeCAD.BoundBox(targetBoundBox.XMin, targetBoundBox.YMin, targetBoundBox.ZMin, 
                                                 targetBoundBox.XMax, self._overallBoundBox.YMax, targetBoundBox.ZMax)
            targetBoundary = targetBoundBox.YMin
            targetSize = targetBoundBox.YLength
        elif motionDirection == base.CartesianMotionDirection.POS_Z:
            elongatedBoundBox = FreeCAD.BoundBox(targetBoundBox.XMin, targetBoundBox.YMin, targetBoundBox.ZMin, 
                                                 targetBoundBox.XMax, targetBoundBox.YMax, self._overallBoundBox.ZMax)
            targetBoundary = targetBoundBox.ZMin
            targetSize = targetBoundBox.ZLength          

        intersectionsDict: typing.Dict[typing.Any, typing.Tuple[float, float]] = {}

        for component in components:
            if not self._isRunning:
                return []
            
            if elongatedBoundBox.intersect(component.Shape.BoundBox):
                intersection = elongatedBoundBox.intersected(component.Shape.BoundBox)
                if intersection.XLength > 0.01 and intersection.YLength > 0.01 and intersection.ZLength > 0.01:
                    if motionDirection == base.CartesianMotionDirection.POS_X:
                        intersectionsDict[component] = (intersection.XMin, intersection.XMax)
                    elif motionDirection == base.CartesianMotionDirection.POS_Y:
                        intersectionsDict[component] = (intersection.YMin, intersection.YMax)
                    elif motionDirection == base.CartesianMotionDirection.POS_Z:
                        intersectionsDict[component] = (intersection.ZMin, intersection.ZMax)

        intervalObstructionsPairs: typing.List[typing.Tuple[typing.Tuple[float, float], 
                                                            typing.Set[typing.Any]]] = []

        if intersectionsDict:
            if not self._isRunning:
                return []

            sortedIntersections: typing.Tuple[typing.Tuple[float, float], ...]
            sortedObstructions: typing.Tuple[typing.Any, ...]
            sortedIntersections, sortedObstructions = zip(*sorted(zip(intersectionsDict.values(), intersectionsDict.keys())))
            
            if not self._isRunning:
                return []
            
            shiftedIntersections: typing.List[typing.Tuple[float, float]] = [(max(targetBoundary, (intersection[0]-targetSize)), 
                                                                              intersection[1]) for intersection in sortedIntersections]
            
            intervalBoundaries: typing.List[float] = sorted(set(itertools.chain.from_iterable(shiftedIntersections)))
            intervals_: typing.List[typing.Tuple[float, float]] = [boundaries for boundaries in zip(intervalBoundaries, intervalBoundaries[1:])]
            
            if not self._isRunning:
                return []
            
            obstructionComponents_: typing.List[typing.Set[typing.Any]] = [{sortedObstructions[index] for index, intersection in enumerate(shiftedIntersections) 
                                                                            if interval[0] < intersection[1] and intersection[0] < interval[1]} for interval in intervals_]
            intervalObstructionsPairs = list(filter(lambda item: len(item[0]) > 0, zip(intervals_, obstructionComponents_)))

        return intervalObstructionsPairs

    def start(self, target: typing.Any, 
                    motionDirection: base.CartesianMotionDirection,
                    method: RefinementMethod) -> typing.List[typing.Tuple[typing.Tuple[float, float], 
                                                                          typing.Set[typing.Any]]]:
        self._isRunning = True
        
        intervalObstructionsPairs: typing.List[typing.Tuple[typing.Tuple[float, float], 
                                                            typing.Set[typing.Any]]] = []

        if method == RefinementMethod.None_:
            interval: typing.Tuple[float, float] = (0.0, 0.0)
            if motionDirection == base.CartesianMotionDirection.POS_X:
                interval = (target.Shape.BoundBox.XMin, self._overallBoundBox.XMax)
            elif motionDirection == base.CartesianMotionDirection.POS_Y:
                interval = (target.Shape.BoundBox.YMin, self._overallBoundBox.YMax)
            elif motionDirection == base.CartesianMotionDirection.POS_Z:
                interval = (target.Shape.BoundBox.ZMin, self._overallBoundBox.ZMax)
            obstructionComponents: typing.Set[typing.Any] = set(filter(lambda c: c != target, self._components))
            intervalObstructionsPairs = [(interval, obstructionComponents)]

        elif method == RefinementMethod.BoundBox:
            intervalObstructionsPairs = self.__potentialObstructionIntervals(
                target, filter(lambda c: c != target, self._components), motionDirection)
        
        self._isRunning = False
        return intervalObstructionsPairs

    def stop(self) -> None:
        self._isRunning = False


class OCCTObstructionDetector:
    def __init__(self, components: typing.Iterable) -> None:
        self._isRunning: bool = False
        self._components: set = set(components)
        self._partPointsMeshDict: typing.Dict = {}
        self._partPointsSampleDict: typing.Dict = {}

    # ********************* START: Getters & Setters *********************

    @property
    def components(self):
        return self._components

    @components.setter
    def components(self, components: typing.Iterable) -> None:
        for component in components:
            self.addComponent(component)

    def addComponent(self, component) -> None:
        self._components.add(component)

    def removeComponent(self, component) -> None:
        self._components.remove(component)

    @property
    def isRunning(self):
        return self._isRunning

    # ********************* END: Getters & Setters *********************

    def __movePart(self, part, displacementVector) -> None:
        part.Placement.move(displacementVector)
    
    def __setPartPlacement(self, part, baseVector, rotationVector) -> None:
        part.Placement = FreeCAD.Placement(baseVector, rotationVector)

    def detectCollisions(self, target: typing.Any, 
                               potentialObstacles: typing.Iterable[typing.Any], 
                               # Solver configuration arguments
                               method: SolverMethod,
                               overlapTolerance:        float = DEF_OVERLAP_TOL,
                               classificationTolerance: float = DEF_CLASSIF_TOL,
                               minDistance:             float = DEF_MIN_DIST,
                               sampleCoefficient:       float = DEF_SAMPLE_COEFF,
                               volumeTolerance:         float = DEF_VOLUME_TOL,
                               **kwargs) -> typing.Set[typing.Any]:
        partPointsMeshDict: typing.Dict = kwargs.get("partPointsMeshDict", {})
        partPointsSampleDict: typing.Dict = kwargs.get("partPointsSampleDict", {})

        collidingObjects: typing.Set[typing.Any] = set()
        for obl in potentialObstacles:
            if not self._isRunning:
                return set()

            # av = target.Shape.BoundBox
            # ov = obl.Shape.BoundBox
            # if av.intersect(ov):
            #     intersection = av.intersected(ov)
            #     if intersection.XLength > 0.01 or intersection.YLength > 0.01 or intersection.ZLength > 0.01:

                    # if len(target.Shape.VertshiftedIntersectionss) > len(obl.Shape.Vertexes):
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

            overlappedSubShapes0, overlappedSubShapes1 = target.Shape.proximity(obl.Shape, overlapTolerance)
            if len(overlappedSubShapes0) > 0 or len(overlappedSubShapes1) > 0:
                if method == SolverMethod.DistToShape:
                    dist, pointPairs, _ = target.Shape.distToShape(obl.Shape)
                    if dist < minDistance:
                        for pointPair in pointPairs:
                            if not self._isRunning:
                                return set()
                            if target.Shape.isInside(pointPair[1], classificationTolerance, False) or obl.Shape.isInside(pointPair[0], classificationTolerance, False):
                                collidingObjects.add(obl)
                                break
                elif method == SolverMethod.MeshInside:
                    boundBox = obl.Shape.BoundBox
                    maxLength: float = min(boundBox.XLength, boundBox.YLength, boundBox.ZLength) * sampleCoefficient
                    if obl.Label not in partPointsMeshDict.keys():
                        partPointsMeshDict[obl.Label] = MeshPart.meshFromShape(Shape=obl.Shape, MaxLength=maxLength).Points
                    meshPoints: typing.List = partPointsMeshDict[obl.Label]
                    for p in random.sample(meshPoints, len(meshPoints)):
                        if not self._isRunning:
                            return set()
                        if target.Shape.isInside(FreeCAD.Vector(p.x, p.y, p.z), classificationTolerance, False):
                            collidingObjects.add(obl)
                            break
                elif method == SolverMethod.GeoDataInside:
                    boundBox = obl.Shape.BoundBox
                    distance: float = min(boundBox.XLength, boundBox.YLength, boundBox.ZLength) * sampleCoefficient
                    if obl.Label not in partPointsSampleDict.keys():
                        partPointsSampleDict[obl.Label] = Aplan.pointSampleShape(obl.Label, distance)
                    samplePoints: typing.List = partPointsSampleDict[obl.Label]
                    point: typing.Tuple[float, float, float]
                    for point in random.sample(samplePoints, len(samplePoints)):
                        if not self._isRunning:
                            return set()
                        if target.Shape.isInside(FreeCAD.Vector(*point), classificationTolerance, False):
                            collidingObjects.add(obl)
                            break
                elif method == SolverMethod.Common:
                    if target.Shape.common(obl.Shape).Volume > volumeTolerance:
                        collidingObjects.add(obl)
                elif method == SolverMethod.Fuse:
                    if target.Shape.fuse(obl.Shape).Volume < (target.Shape.Volume + obl.Shape.Volume - volumeTolerance):
                        collidingObjects.add(obl)
        
        return collidingObjects

    def start(self, target: typing.Any,
                    motionDirection: base.CartesianMotionDirection,
                    # Solver configuration arguments
                    method: SolverMethod,
                    variableStepSizeEnabled: bool  = DEF_VAR_STEP_SIZE_ENABLED,
                    fixedStepSize:           float = DEF_FIXED_STEP_SIZE,
                    minStepSize:             float = DEF_MIN_STEP_SIZE,
                    stepSizeCoefficient:     float = DEF_STEP_SIZE_COEFF,
                    minDistance:             float = DEF_MIN_DIST,
                    overlapTolerance:        float = DEF_OVERLAP_TOL,
                    classificationTolerance: float = DEF_CLASSIF_TOL,
                    volumeTolerance:         float = DEF_VOLUME_TOL,
                    sampleCoefficient:       float = DEF_SAMPLE_COEFF,
                    # Refinement arguments
                    intervalObstructionsPairs: typing.Optional[typing.Iterable[typing.Tuple[typing.Tuple[float, float], 
                                                                                            typing.Set[typing.Any]]]] = None,
                    # Part manipulation functions
                    fMovePart: typing.Optional[typing.Callable] = None,
                    fSetPartPlacement: typing.Optional[typing.Callable] = None) -> typing.Set[typing.Any]:
        self._isRunning = True

        movePart: typing.Callable = fMovePart or self.__movePart
        setPartPlacement: typing.Callable = fSetPartPlacement or self.__setPartPlacement
        
        intervalObstructionsPairs_: typing.Iterable[typing.Tuple[typing.Tuple[float, float], typing.Set[typing.Any]]] = \
            intervalObstructionsPairs or OCCTRefiner(self._components).start(target, motionDirection, RefinementMethod.None_)
         
        targetStartPosition = target.Placement

        offset: float = 0.0
        if motionDirection == base.CartesianMotionDirection.POS_X:
            offset = target.Placement.Base[0]-target.Shape.BoundBox.XMin
        elif motionDirection == base.CartesianMotionDirection.POS_Y:
            offset = target.Placement.Base[1]-target.Shape.BoundBox.YMin
        elif motionDirection == base.CartesianMotionDirection.POS_Z:
            offset = target.Placement.Base[2]-target.Shape.BoundBox.ZMin
        
        obstructions: typing.Set[typing.Any] = set()

        obstructionInterval: typing.Tuple[float, float]
        potentialObstructions: typing.Set[typing.Any]
        for obstructionInterval, potentialObstructions in intervalObstructionsPairs_:
            if not self._isRunning:
                return set()

            stepSize: float
            if variableStepSizeEnabled:
                stepSize = max((obstructionInterval[1]-obstructionInterval[0]) * stepSizeCoefficient, minStepSize)
            else:
                stepSize = fixedStepSize

            if motionDirection == base.CartesianMotionDirection.POS_X:
                baseVector = FreeCAD.Vector(obstructionInterval[0]+offset, targetStartPosition.Base[1], targetStartPosition.Base[2])
            elif motionDirection == base.CartesianMotionDirection.POS_Y:
                baseVector = FreeCAD.Vector(targetStartPosition.Base[0], obstructionInterval[0]+offset, targetStartPosition.Base[2])
            elif motionDirection == base.CartesianMotionDirection.POS_Z:
                baseVector = FreeCAD.Vector(targetStartPosition.Base[0], targetStartPosition.Base[1], obstructionInterval[0]+offset)
            setPartPlacement(target, baseVector, targetStartPosition.Rotation)

            targetPosition = obstructionInterval[0]
            while targetPosition < obstructionInterval[1]:
                if not self._isRunning:
                    return set()
                
                remainingObstructions: typing.Set[typing.Any] = potentialObstructions.difference(obstructions)
                if remainingObstructions == set():
                    break

                if motionDirection == base.CartesianMotionDirection.POS_X:
                    movePart(target, FreeCAD.Vector(stepSize, 0.0, 0.0))
                    targetPosition = target.Shape.BoundBox.XMin
                elif motionDirection == base.CartesianMotionDirection.POS_Y:
                    movePart(target, FreeCAD.Vector(0.0, stepSize, 0.0))
                    targetPosition = target.Shape.BoundBox.YMin
                elif motionDirection == base.CartesianMotionDirection.POS_Z:
                    movePart(target, FreeCAD.Vector(0.0, 0.0, stepSize))
                    targetPosition = target.Shape.BoundBox.ZMin

                if not self._isRunning:
                    return set()

                obstructions.update(self.detectCollisions(target,
                                                          remainingObstructions,
                                                          method,
                                                          overlapTolerance,
                                                          classificationTolerance,
                                                          minDistance,
                                                          sampleCoefficient,
                                                          volumeTolerance,
                                                          partPointsMeshDict = self._partPointsMeshDict,
                                                          partPointsSampleDict = self._partPointsSampleDict))

        setPartPlacement(target, targetStartPosition.Base, targetStartPosition.Rotation)

        self._isRunning = False
        return obstructions

    def stop(self) -> None:
        self._isRunning = False


class OCCTSolver:
    def __init__(self, components: typing.Iterable[typing.Any], 
                       motionDirections: typing.Iterable[base.CartesianMotionDirection],
                       linearDeflection: float = DEF_LIN_DEFLECT) -> None:
        self._isRunning: bool = False

        if not FreeCAD.GuiUp:
            # In order for TopoShapePy::proximity to work, every shape's faces need to be tessellated. 
            # This is not done by default when FreeCAD's GUI is not running. 
            # Source: https://forum.freecadweb.org/viewtopic.php?t=22857
            for component in components:
                self.__tessellateComponent(component, linearDeflection)
        self._components: set = set(components)
        
        self._nonRedundantMotionDirs: typing.Set[base.CartesianMotionDirection] = {base.CartesianMotionDirection(abs(motionDir_.value)) 
                                                                                   for motionDir_ in motionDirections}

        self._refiner: OCCTRefiner = OCCTRefiner(self._components)
        self._obstructionDetector: OCCTObstructionDetector = OCCTObstructionDetector(self._components)

    # ********************* START: Getters & Setters *********************

    @property
    def isRunning(self):
        return self._isRunning

    # ********************* END: Getters & Setters *********************

    def __tessellateComponent(self, component, linearDeflection: float) -> None:
        for face in component.Shape.Faces:
            face.tessellate(linearDeflection)

    def refine(self, method: RefinementMethod, 
                     configParam: typing.Dict) -> typing.Dict[base.CartesianMotionDirection, 
                                                              typing.Dict[str, 
                                                                          typing.List[typing.Tuple[typing.Tuple[float, float], 
                                                                                                   typing.Set[typing.Any]]]]]:
        self._isRunning = True

        intervalObstructionsDict: typing.Dict[base.CartesianMotionDirection, 
                                              typing.Dict[str, 
                                                          typing.List[typing.Tuple[typing.Tuple[float, float], 
                                                                                   typing.Set[typing.Any]]]]] = {}
        
        motionDirection: base.CartesianMotionDirection
        for motionDirection in self._nonRedundantMotionDirs:
            intervalObstructionsDict[motionDirection] = {}          
            for target in self._components:
                if not self._isRunning:
                    return {}

                intervalObstructionsDict[motionDirection][target.Label] = self._refiner.start(target, motionDirection, method)

        self._isRunning = False
        return intervalObstructionsDict

    def solve(self, method: SolverMethod,
                    configParam: typing.Dict, 
                    configParamGeneral: typing.Dict,
                    intervalObstructionsDict: typing.Optional[typing.Dict] = None,
                    # Part manipulation functions
                    fMovePart: typing.Optional[typing.Callable] = None,
                    fSetPartPlacement: typing.Optional[typing.Callable] = None) -> typing.Dict[base.CartesianMotionDirection, typing.Set[typing.Tuple[str, str]]]:
        self._isRunning = True

        geomConstraints: typing.Dict[base.CartesianMotionDirection, 
                                     typing.Set[typing.Tuple[str, str]]] = {motionDir: set() for motionDir in self._nonRedundantMotionDirs}

        intervalObstructionsDict_: typing.Dict = intervalObstructionsDict or self.refine(RefinementMethod.None_, {})

        motionDirection: base.CartesianMotionDirection
        for motionDirection in self._nonRedundantMotionDirs:
            for target in self._components:
                if not self._isRunning:
                    return {}
                
                obstructions: typing.Set[typing.Any] = self._obstructionDetector.start(target, 
                                                                                       motionDirection, 
                                                                                       method,
                                                                                       **configParamGeneral,
                                                                                       **configParam,
                                                                                       intervalObstructionsPairs=intervalObstructionsDict_[motionDirection][target.Label],
                                                                                       fMovePart=fMovePart,
                                                                                       fSetPartPlacement=fSetPartPlacement)

                geomConstraints[motionDirection].update({(target.Label, component.Label) for component in obstructions})
        
        self._isRunning = False
        return geomConstraints

    def stop(self) -> None:
        self._isRunning = False
        if self._refiner.isRunning:
            self._refiner.stop()
        if self._obstructionDetector.isRunning:
            self._obstructionDetector.stop()
