/***************************************************************************
 *                                                                         *
 *   Copyright (c) 2008 Jürgen Riegel <juergen.riegel@web.de>              *
 *   Copyright (c) 2021 Martijn Cramer <martijn.cramer@outlook.com>        *
 *                                                                         *
 *   This file is part of the FreeCAD CAx development system.              *
 *                                                                         *
 *   This library is free software; you can redistribute it and/or         *
 *   modify it under the terms of the GNU Library General Public           *
 *   License as published by the Free Software Foundation; either          *
 *   version 2 of the License, or (at your option) any later version.      *
 *                                                                         *
 *   This library  is distributed in the hope that it will be useful,      *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU Library General Public License for more details.                  *
 *                                                                         *
 *   You should have received a copy of the GNU Library General Public     *
 *   License along with this library; see the file COPYING.LIB. If not,    *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,         *
 *   Suite 330, Boston, MA  02111-1307, USA                                *
 *                                                                         *
 ***************************************************************************/

#include "PreCompiled.hpp"
#ifndef _PreComp_
#include <Python.h>
#endif

#include <CXX/Extensions.hxx>
#include <CXX/Objects.hxx>

#include <App/Application.h>
#include <App/ComplexGeoData.h>
#include <App/Document.h>
#include <App/DocumentObject.h>
#include <App/DocumentObjectPy.h>
#include <App/GeoFeature.h>
#include <App/PropertyGeo.h>
#include <Base/Console.h>
#include <Base/GeometryPyCXX.h>
#include <Base/PyObjectBase.h>
#include <Base/Vector3D.h>
#include <Mod/Part/App/OCCError.h>

namespace Aplan
{
    class Module : public Py::ExtensionModule<Module>
    {
    public:
        Module() : Py::ExtensionModule<Module>("Aplan")
        {
            add_varargs_method("pointSampleShape",&Module::pointSampleShape,
                "Creates a point cloud of a part's shape and returns the list of sampled points\n"
                "\n"
                "pointSampleShape(label, distance) -> list\n"
                "\n"
                "Args:\n"
                "    label (required, string): the label of the part to sample\n"
                "    distance (required, float): the maximum distance between the sampled points\n"
            );
            initialize("This module is the APLAN module."); // register with Python
        }

        virtual ~Module() {}

    private:
        virtual Py::Object invoke_method_varargs(void *method_def, const Py::Tuple &args)
        {
            try
            {
                return Py::ExtensionModule<Module>::invoke_method_varargs(method_def, args);
            }
            catch (const Standard_Failure &e)
            {
                std::string str;
                Standard_CString msg = e.GetMessageString();
                str += typeid(e).name();
                str += " ";
                if (msg)
                {
                    str += msg;
                }
                else
                {
                    str += "No OCCT Exception Message";
                }
                throw Py::Exception(Part::PartExceptionOCCError, str);
            }
            catch (const Base::Exception &e)
            {
                throw Py::RuntimeError(e.what());
            }
            catch (const std::exception &e)
            {
                throw Py::RuntimeError(e.what());
            }
        }

        Py::Object pointSampleShape(const Py::Tuple& args)
        {
            const char *label{};
            double distance{0.0};
            if (!PyArg_ParseTuple(args.ptr(), "sd", &label, &distance))
            {
                throw Py::Exception(PyExc_TypeError, "pointSampleShape: 1st parameter must be a string, 2nd parameter must be a float.");
            }

            std::vector<Base::Vector3d> vertices{};
            std::vector<App::DocumentObject *> objects = App::GetApplication().getActiveDocument()->getObjects();
            for (std::vector<App::DocumentObject *>::iterator it = objects.begin(); it != objects.end(); ++it)
            {
                if ((*it)->Label.getStrValue() == label)
                {
                    const App::PropertyComplexGeoData *prop = static_cast<App::GeoFeature *>(*it)->getPropertyOfGeometry();
                    if (prop)
                    {
                        const Data::ComplexGeoData *data = prop->getComplexData();
                        std::vector<Base::Vector3d> normals;
                        data->getPoints(vertices, normals, static_cast<float>(distance));
                    }
                    break;
                }
            }

            Py::List pyVertices;
            for (Base::Vector3d vertex : vertices)
            {
                pyVertices.append(Py::Vector(vertex));
            }
            return pyVertices;
        }

    };

    PyObject *initModule()
    {
        return (new Module)->module().ptr();
    }

} // namespace Aplan
