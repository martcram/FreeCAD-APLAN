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

from aplantools import aplanutils
try:
    import aplansolvers.aplan_obstruction_detectors.base_obstruction_detector as base
    import enum
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


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
    return aplanutils.createObject(doc, name, OCCT, VPOCCT)


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


class VPOCCT(base.IVPObstructionDetector):
    def setEdit(self, vobj, mode=0):
        return True

    def unsetEdit(self, vobj, mode=0):
        return True

    def doubleClicked(self, vobj):
        return True
