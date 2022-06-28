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
    import FreeCAD
    if FreeCAD.GuiUp:
        import FreeCADGui
    import itertools
    from PySide2 import QtCore, QtWidgets
    import typing
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
        task = _TaskPanel(vobj.Object)
        FreeCADGui.Control.showDialog(task)
        return True

    def unsetEdit(self, vobj, mode=0):
        FreeCADGui.Control.closeDialog()
        return True

    def doubleClicked(self, vobj):
        guidoc = FreeCADGui.getDocument(vobj.Object.Document)
        # check if another VP is in edit mode
        # https://forum.freecadweb.org/viewtopic.php?t=13077#p104702
        if not guidoc.getInEdit():
            guidoc.setEdit(vobj.Object.Name)
        else:
            message = "Active Task Dialog found! Please close this one before opening a new one!"
            QtWidgets.QMessageBox.critical(None, "Error in tree view", message)
            FreeCAD.Console.PrintError(message + "\n")
        return True


class _TaskPanel(base.ITaskPanel):
    """
    The TaskPanel for APLAN ConnectionDetectorSwellOCCT object
    """

    def __init__(self, swellOCCTObject) -> None:
        super(_TaskPanel, self).__init__(swellOCCTObject)

        # Read and/or calculate property values
        #* General properties
        self._parts: typing.Dict = {part.Label: part for part in FreeCAD.ActiveDocument.findObjects("Part::Feature")}
        self._excludedPartsDict: typing.Dict = {}
        self._noExcludedParts: int = 0
        self._compoundsDict: typing.Dict = {}
        self._noCompounds: int = 0
        if self._analysis.PartFilterObjects:
            self._excludedPartsDict = {excludedPart.Label: excludedPart for partFilter in self._analysis.PartFilterObjects 
                                       for excludedPart in partFilter.ExcludedParts}
            self._noExcludedParts = len(self._excludedPartsDict)
            self._compoundsDict = {compound.Label: compound for partFilter in self._analysis.PartFilterObjects 
                                   for compound in partFilter.Compounds}
            self._noCompounds = len(self._compoundsDict)
        excludedPartLabels: typing.Set[str] = set(self._excludedPartsDict.keys())
        compoundsLabels: typing.Set[str] = set(self._compoundsDict.keys())
        groupedPartLabels: typing.Set[str] = {part.Label for compound in self._compoundsDict.values() for part in compound.Links}
        self._disjointPartsDict: typing.Dict = {disjointPartLabel: self._parts[disjointPartLabel] 
                                                for disjointPartLabel in set(self._parts.keys()).difference(
                                                    excludedPartLabels.union(groupedPartLabels).union(compoundsLabels))}
        disjointPartLabels: typing.Set[str] = set(self._disjointPartsDict.keys())
        self._noDisjointParts: int = len(disjointPartLabels)
        self._noParts: int = len(disjointPartLabels) + len(excludedPartLabels) + len(groupedPartLabels)
        self._componentsDict: typing.Dict = {**self._disjointPartsDict, **self._compoundsDict}
        self._computationTime: float = 0.0
        #* Refinement properties
        for refinementMethod in RefinementMethod:
            if self.obj.RefinementMethod == refinementMethod.value[0]:
                self._refinementMethod: RefinementMethod = refinementMethod
                break
        self._configParamRefinement: typing.Dict[RefinementMethod, typing.Set[str]] = {}
        self._qWidgetDictRefinement: typing.Dict[str, typing.Dict] = {}
        #* Solver properties
        self._variableStepSizeEnabled: bool = bool(self.obj.VariableStepSizeEnabled)
        self._stepSizeCoefficient: float = float(self.obj.StepSizeCoefficient)
        self._minStepSize: float = float(self.obj.MinStepSize)
        self._fixedStepSize: float = float(self.obj.FixedStepSize)
        self._motionDirections: typing.Set[base.CartesianMotionDirection] = {base.CartesianMotionDirection[motionDir.upper()]
                                                                             for motionDir in self.obj.MotionDirections}
        for solverMethod in SolverMethod:
            if self.obj.SolverMethod == solverMethod.value[0]:
                self._solverMethod: SolverMethod = solverMethod
                break
        self._minDistance: float = float(self.obj.MinDistance)
        self._overlapTolerance: float = float(self.obj.OverlapTolerance)
        self._classificationTolerance: float = float(self.obj.ClassificationTolerance)
        self._volumeTolerance: float = float(self.obj.VolumeTolerance)
        self._sampleCoefficient: float = float(self.obj.SampleCoefficient)
        self._configParamSolver: typing.Dict[SolverMethod, typing.Set[str]] = {SolverMethod.DistToShape:   {"overlapTolerance", "minDistance", "classificationTolerance"},
                                                                               SolverMethod.MeshInside:    {"overlapTolerance", "classificationTolerance", "sampleCoefficient"},
                                                                               SolverMethod.GeoDataInside: {"overlapTolerance", "classificationTolerance", "sampleCoefficient"},
                                                                               SolverMethod.Common:        {"overlapTolerance", "volumeTolerance"},
                                                                               SolverMethod.Fuse:          {"overlapTolerance", "volumeTolerance"}}
        self._qWidgetDictSolver: typing.Dict[str, typing.Dict] = {"classificationTolerance": {"label": self.form.l_label_classification_tolerance,
                                                                                              "value": self.form.dsb_classification_tolerance},
                                                                  "minDistance": {"label": self.form.l_label_min_distance, 
                                                                                  "value": self.form.dsb_min_distance},
                                                                  "overlapTolerance": {"label": self.form.l_label_overlap_tolerance,
                                                                                       "value": self.form.dsb_overlap_tolerance},
                                                                  "sampleCoefficient": {"label": self.form.l_label_sample_coefficient, 
                                                                                        "value": self.form.dsb_sample_coefficient},
                                                                  "volumeTolerance": {"label": self.form.l_label_volume_tolerance, 
                                                                                      "value": self.form.dsb_volume_tolerance}}

        # Update task panel form
        #* General properties
        self.form.l_label_parts.setToolTip(
            "The total amount of parts in this document.")
        self.form.l_parts.setText(str(self._noParts))
        self.form.l_label_disjoint_parts.setToolTip(
            "The amount of parts that are not compounded/grouped i.e. disjointed.")
        self.form.l_disjoint_parts.setText(str(self._noDisjointParts))
        self.form.l_label_compounds.setToolTip(
            "The amount of compounds created in this analysis container.")
        self.form.l_compounds.setText(str(self._noCompounds))
        self.form.l_label_excluded_parts.setToolTip(
            "The amount of parts that were excluded from analysis.")
        self.form.l_excluded_parts.setText(str(self._noExcludedParts))
        self.form.l_label_type.setToolTip(
            "The type of solver selected for detecting part connections.")
        self.form.l_type.setText(self._solverType)
        #* Refinement properties
        index1: int
        for index1, refinementMethod in enumerate(RefinementMethod):
            self.form.cb_refinement_method.insertItem(index1, refinementMethod.value[0])
            self.form.cb_refinement_method.setItemData(index1, refinementMethod.value[1], QtCore.Qt.ToolTipRole)
        self.__switchRefinementMethod(self._refinementMethod.value[0])
        self.form.cb_refinement_method.setCurrentText(self._refinementMethod.value[0])
        #* Solver properties
        self.form.cb_variable_step_size.setChecked(self._variableStepSizeEnabled)
        self.__toggleVariableStepSize((QtCore.Qt.Unchecked, QtCore.Qt.Checked)[self._variableStepSizeEnabled])
        self.form.dsb_step_size_coeff.setValue(self._stepSizeCoefficient)
        self.form.dsb_min_step_size.setValue(self._minStepSize)
        self.form.dsb_fixed_step_size.setValue(self._fixedStepSize)
        index2: int
        for index2, solverMethod in enumerate(SolverMethod):
            self.form.cb_solver_method.insertItem(index2, solverMethod.value[0])
            self.form.cb_solver_method.setItemData(index2, solverMethod.value[1], QtCore.Qt.ToolTipRole)
        self.__switchSolverMethod(self._solverMethod.value[0])
        self.form.cb_solver_method.setCurrentText(self._solverMethod.value[0])
        motionDir_: base.CartesianMotionDirection
        for motionDir_ in self._motionDirections:
            self.form.findChild(QtWidgets.QCheckBox,
                                "cb_{}".format(motionDir_.name.lower())).setChecked(True)
        self.form.l_time.setText("{} s".format(self._computationTime))

        # Connect signals and slots
        #* Refinement properties
        self.form.cb_refinement_method.currentTextChanged.connect(self.__switchRefinementMethod)
        for qWidget in {widgets["value"] for widgets in self._qWidgetDictRefinement.values()}:
            qWidget.valueChanged.connect(self.__readConfigFieldsRefinement)
        #* Solver properties
        self.form.cb_variable_step_size.stateChanged.connect(self.__toggleVariableStepSize)
        self.form.dsb_step_size_coeff.valueChanged.connect(self.__readInputFields)
        self.form.dsb_min_step_size.valueChanged.connect(self.__readInputFields)
        self.form.dsb_fixed_step_size.valueChanged.connect(self.__readInputFields)
        self.form.cb_solver_method.currentTextChanged.connect(self.__switchSolverMethod)
        for qWidget in {widgets["value"] for widgets in self._qWidgetDictSolver.values()}:
            qWidget.valueChanged.connect(self.__readConfigFieldsSolver)
        motionDirection_: base.CartesianMotionDirection
        for motionDirection_ in self._motionDirections:
            self.form.findChild(QtWidgets.QCheckBox,
                                "cb_{}".format(motionDirection_.name.lower())
                                ).stateChanged.connect(lambda state, objName=motionDirection_.name: 
                                                       self.__readCheckBoxState(state, objName))
        self.form.btn_run.clicked.connect(self.__run)

    def getStandardButtons(self) -> int:
        button_value = int(QtWidgets.QDialogButtonBox.Cancel)
        return button_value

    def reject(self) -> bool:
        self.__writeProperties()
        self.obj.ViewObject.Document.resetEdit()
        self.obj.Document.recompute()
        return True

    def __readCheckBoxState(self, state: int, objectName: str) -> None:
        motionDirection: base.CartesianMotionDirection = base.CartesianMotionDirection[objectName.upper()]
        if state == QtCore.Qt.Checked:
            self._motionDirections.add(motionDirection)
        else:
            self._motionDirections.remove(motionDirection)

    def __readConfigFieldsRefinement(self) -> None:
        paramLabel: str
        for paramLabel, qWidgets in self._qWidgetDictRefinement.items():
            self.__dict__["_{}".format(paramLabel)] = qWidgets["value"].value()

    def __readConfigFieldsSolver(self) -> None:
        paramLabel: str
        for paramLabel, qWidgets in self._qWidgetDictSolver.items():
            self.__dict__["_{}".format(paramLabel)] = qWidgets["value"].value()

    def __readInputFields(self) -> None:
        self._stepSizeCoefficient = float(self.form.dsb_step_size_coeff.text())
        self._minStepSize = float(self.form.dsb_min_step_size.text())
        self._fixedStepSize = float(self.form.dsb_fixed_step_size.text())

    def __run(self) -> None:
        pass

    def __switchSolverMethod(self, solverMethod: str) -> None:
        for method in SolverMethod:
            if solverMethod == method.value[0]:
                self._solverMethod = method
                break
        for qWidget in set(itertools.chain.from_iterable([widgets.values() for widgets in self._qWidgetDictSolver.values()])):
            qWidget.setHidden(True)
        param_: str
        for param_ in self._configParamSolver.get(self._solverMethod, set()):
            self._qWidgetDictSolver[param_]["value"].setValue(self.__dict__["_{}".format(param_)])
            for qWidget in self._qWidgetDictSolver[param_].values():
                qWidget.setHidden(False)

    def __switchRefinementMethod(self, refinementMethod: str) -> None:
        for method in RefinementMethod:
            if refinementMethod == method.value[0]:
                self._refinementMethod = method
                break
        for qWidget in set(itertools.chain.from_iterable([widgets.values() for widgets in self._qWidgetDictRefinement.values()])):
            qWidget.setHidden(True)
        param_: str
        for param_ in self._configParamRefinement.get(self._refinementMethod, set()):
            self._qWidgetDictRefinement[param_]["value"].setValue(self.__dict__["_{}".format(param_)])
            for qWidget in self._qWidgetDictRefinement[param_].values():
                qWidget.setHidden(False)
        
        if self._refinementMethod == RefinementMethod.None_:
            self.form.l_label_variable_step_size.setEnabled(False)
            self.form.cb_variable_step_size.setEnabled(False)
            self.form.cb_variable_step_size.setCheckState(QtCore.Qt.Unchecked)
            self.__toggleVariableStepSize(QtCore.Qt.Unchecked)
        elif self._refinementMethod == RefinementMethod.BoundBox:
            self.form.l_label_variable_step_size.setEnabled(True)
            self.form.cb_variable_step_size.setEnabled(True)

    def __toggleVariableStepSize(self, state: QtCore.Qt.CheckState) -> None:
        self._variableStepSizeEnabled = (state == QtCore.Qt.Checked)
        if self._variableStepSizeEnabled:
            self.form.l_label_step_size_coeff.setHidden(False)
            self.form.dsb_step_size_coeff.setHidden(False)
            self.form.l_label_min_step_size.setHidden(False)
            self.form.dsb_min_step_size.setHidden(False)
            self.form.l_label_fixed_step_size.setHidden(True)
            self.form.dsb_fixed_step_size.setHidden(True)
        else:
            self.form.l_label_step_size_coeff.setHidden(True)
            self.form.dsb_step_size_coeff.setHidden(True)
            self.form.l_label_min_step_size.setHidden(True)
            self.form.dsb_min_step_size.setHidden(True)
            self.form.l_label_fixed_step_size.setHidden(False)
            self.form.dsb_fixed_step_size.setHidden(False)

    def __writeProperties(self) -> None:
        self.obj.RefinementMethod = self._refinementMethod.value[0]
        self.obj.VariableStepSizeEnabled = self._variableStepSizeEnabled
        self.obj.StepSizeCoefficient = self._stepSizeCoefficient
        self.obj.MinStepSize = self._minStepSize
        self.obj.FixedStepSize = self._fixedStepSize
        self.obj.SolverMethod = self._solverMethod.value[0]
        self.obj.MinDistance = self._minDistance
        self.obj.ClassificationTolerance = self._classificationTolerance
        self.obj.OverlapTolerance = self._overlapTolerance
        self.obj.VolumeTolerance = self._volumeTolerance
        self.obj.SampleCoefficient = self._sampleCoefficient
        self.obj.MotionDirections = [motionDir.name for motionDir in self._motionDirections]
