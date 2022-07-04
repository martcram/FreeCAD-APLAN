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
    import time
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

    def __handleError(self, error: typing.Tuple) -> None:
        aplanutils.displayAplanError(*error)

    def __processOutput(self, output: typing.Dict) -> None:
        pass

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

    def __reportProgress(self, progress: typing.Dict) -> None:
        self.form.te_output.setTextColor(base.MessageType(progress["type"]).value)
        self.form.te_output.append(progress["msg"])
        self.form.te_output.setTextColor(base.MessageType.INFO.value)

    def __run(self) -> None:
        if self._solverThread is None or not self._solverThread.isRunning():
            # Init
            configParamRefinement: typing.Dict = {param: self.__dict__["_{}".format(param)] 
                                                  for param in self._configParamRefinement.get(self._refinementMethod, set())}
            configParamSolver: typing.Dict = {param: self.__dict__["_{}".format(param)] 
                                              for param in self._configParamSolver.get(self._solverMethod, set())}
            inputParams: typing.Dict = {"componentsDict": self._componentsDict,
                                        "motionDirections": self._motionDirections,
                                        "refinementMethod": self._refinementMethod,
                                        "configParamRefinement": configParamRefinement,
                                        "solverMethod": self._solverMethod,
                                        "configParamSolver": configParamSolver}

            self._solverThread = QtCore.QThread()
            self._worker: Worker = Worker(self.obj.Type, inputParams)
            self._worker.moveToThread(self._solverThread)

            # Connect signals and slots
            self._solverThread.started.connect(self._worker.run)
            self._solverThread.finished.connect(self.__threadFinished)
            self._solverThread.finished.connect(self._solverThread.deleteLater)
            self._worker.progress.connect(self.__reportProgress)
            self._worker.finished.connect(self.__processOutput)
            self._worker.finished.connect(self._solverThread.quit)
            self._worker.finished.connect(self._worker.deleteLater)
            self._worker.error.connect(self.__handleError)

            # Start solver thread
            self._solverThread.start()
            self.__threadStarted()

        elif self._solverThread is not None and self._solverThread.isRunning() and self._worker.isRunning:
            self.form.btn_run.setText("Terminating ...")
            self.form.btn_run.setStyleSheet("background-color: {}".format(self._COLOR_TERMINATING))

            self._worker.stop()
            self._solverThread.quit()

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

    def __threadFinished(self) -> None:
        self.form.btn_run.setText("Run")
        self.form.btn_run.setStyleSheet("background-color: {}".format(self._COLOR_RUN))
        self._solverThread = None

    def __threadStarted(self) -> None:
        self.form.btn_run.setText("Abort")
        self.form.btn_run.setStyleSheet("background-color: {}".format(self._COLOR_ABORT))

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


class OCCTSolver:
    def __init__(self, components: typing.List, motionDirections: typing.Set[base.CartesianMotionDirection]) -> None:
        self._isRunning: bool = True
        self.setComponents(components)
        self._nonRedundantMotionDirs: typing.Set[base.CartesianMotionDirection] = {base.CartesianMotionDirection(abs(motionDir_.value)) 
                                                                                   for motionDir_ in motionDirections}

    def setComponents(self, components: typing.List) -> None:
        self._componentsDict = {component.Label: component for component in components}

    def refine(self, method: RefinementMethod, configParam: typing.Dict) -> typing.Dict:
        overallBoundbox = FreeCAD.BoundBox()
        for component in self._componentsDict.values():
            overallBoundbox.add(component.Shape.BoundBox)
        if not self._isRunning:
                return {}
        componentsIntervalPairs: typing.Dict = {}
        motionDirection_: base.CartesianMotionDirection
        for motionDirection_ in self._nonRedundantMotionDirs:
            if not self._isRunning:
                return {}
            componentsIntervalPairs[motionDirection_.name] = {}
            for target in self._componentsDict.values():
                if not self._isRunning:
                    return {}
                intersectionComponents: typing.List[typing.List] = [comp for comp in self._componentsDict.values() if comp != target]
                intervals: typing.List[typing.List[float]] = []
                if method == RefinementMethod.None_:
                    if motionDirection_ == base.CartesianMotionDirection.POS_X:
                        intervals.append([target.Shape.BoundBox.XMin, overallBoundbox.XMax])
                    elif motionDirection_ == base.CartesianMotionDirection.POS_Y:
                        intervals.append([target.Shape.BoundBox.YMin, overallBoundbox.YMax])
                    elif motionDirection_ == base.CartesianMotionDirection.POS_Z:
                        intervals.append([target.Shape.BoundBox.ZMin, overallBoundbox.ZMax])
                elif method == RefinementMethod.BoundBox:
                    intersectionComponents, intervals = self.__findPotentialObstacles(target, {component for component in self._componentsDict.values() 
                                                                                               if component.Label != target.Label}, 
                                                                                      motionDirection_, overallBoundbox)
                componentsIntervalPairs[motionDirection_.name][target.Label] = list(zip(intersectionComponents, intervals))
        return componentsIntervalPairs

    def stop(self) -> None:
        self._isRunning = False

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


class Worker(base.BaseWorker):
    def __init__(self, detectorType: str, inputParams: typing.Dict) -> None:
        super(Worker, self).__init__(detectorType)
        self._inputParams: typing.Dict = inputParams
        self._isRunning: bool = False
        self._componentsDict: typing.Dict = self._inputParams["componentsDict"]
        self._motionDirections: typing.Set[base.CartesianMotionDirection] = self._inputParams["motionDirections"]
        self._refinementMethod: RefinementMethod = self._inputParams["refinementMethod"]
        self._configParamRefinement: typing.Dict = self._inputParams["configParamRefinement"]
        self._solver: OCCTSolver = OCCTSolver(list(self._componentsDict.values()), self._motionDirections)

    def run(self) -> None:
        self.progress.emit({"msg": ">>> STARTED",
                            "type": base.MessageType.INFO})
        self._isRunning = True
        computationTime: float = 0.0

        try:
            self.progress.emit({"msg": "====== Refining ======",
                                "type": base.MessageType.INFO})
            self.progress.emit({"msg": "Performing the {} refinement method".format(self._refinementMethod.value[0]),
                                "type": base.MessageType.INFO})
            time0: float = time.perf_counter()

            componentsIntervalPairs: typing.Dict = self._solver.refine(self._refinementMethod, self._configParamRefinement)

            time1: float = time.perf_counter()
            computationTime += time1-time0

            noPotentialObstructions: int = 0
            motionDirLabel: str
            targetDict: typing.Dict
            for motionDirLabel, targetDict in componentsIntervalPairs.items():
                self.progress.emit({"msg": "*** Motion direction: {} ***".format(motionDirLabel),
                                    "type": base.MessageType.INFO})
                targetLabel: str
                compIntervalPairs: typing.List
                for targetLabel, compIntervalPairs in targetDict.items():
                    noIntersectionComponents: int = len(set(itertools.chain.from_iterable([pair[0] for pair in compIntervalPairs])))
                    noPotentialObstructions += noIntersectionComponents
                    self.progress.emit({"msg": "\tFound {} potential obstructions for {}.".format(noIntersectionComponents, targetLabel),
                                        "type": base.MessageType.INFO})
            self.progress.emit({"msg": "*******\nFound {} potential obstructions in total.".format(noPotentialObstructions),
                                        "type": base.MessageType.INFO})
            self.progress.emit({"msg": "> Done: {:.3f}s".format(time1-time0),
                                "type": base.MessageType.INFO})

            if not self._isRunning:
                self.__abort()
                return

            self.progress.emit({"msg": ">>> FINISHED",
                                "type": base.MessageType.INFO})

            self._isRunning = False
            self.finished.emit({"time": computationTime,
                                "constraints": []})
        
        except Exception as e:
            self.progress.emit({"msg": ">>> ERROR\n{}\nERROR <<<".format(e),
                                "type": base.MessageType.ERROR})
            self.__abort()
  
    def stop(self) -> None:
        self._isRunning = False
        self._solver.stop()

    def __abort(self) -> None:
        self._isRunning = False
        self.progress.emit({"msg": ">>> ABORTED",
                            "type": base.MessageType.WARNING})
        self.finished.emit({})
