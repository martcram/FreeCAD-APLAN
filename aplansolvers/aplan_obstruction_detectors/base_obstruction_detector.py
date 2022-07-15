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

__title__ = "Abstract base classes of the FreeCAD APLAN ObstructionDetector object"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

try:
    import abc
    import enum
    import typing
except ImportError as ie:
    print("Missing dependency! Please install the following Python module: {}".format(str(ie.name or "")))


class IObstructionDetector(metaclass=abc.ABCMeta):
    BaseType = "Aplan::ObstructionDetectorPython"

    def __init__(self, obj):
        obj.Proxy = self
        if not hasattr(obj, "Type"):
            obj.addProperty(
                "App::PropertyString",
                "Type",
                "Obstruction detector",
                "Type of obstruction detector"
            )
            obj.setEditorMode("Type", 1)  # read-only

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class IMotionDirection(enum.Enum):
    def __init__(self, _: int, unitVector: typing.Tuple[float, float, float]):
        self._unitVector_: typing.Tuple[float, float, float] = unitVector

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __repr__(self) -> str:
        return "{}.{}".format(self.__class__.__name__, self.name)

    @property
    def unitVector(self) -> typing.Tuple[float, float, float]:
        return self._unitVector_


class UndefMotionDirection(IMotionDirection):
    UNDEF = (0, (0.0,  0.0,  0.0))


class CartesianMotionDirection(IMotionDirection):
    NEG_X = (-1, (-1.0,  0.0,  0.0))
    POS_X = ( 1, ( 1.0,  0.0,  0.0))
    NEG_Y = (-2, ( 0.0, -1.0,  0.0))
    POS_Y = ( 2, ( 0.0,  1.0,  0.0))
    NEG_Z = (-3, ( 0.0,  0.0, -1.0))
    POS_Z = ( 3, ( 0.0,  0.0,  1.0))
