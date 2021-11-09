/***************************************************************************
 *                                                                         *
 *   Copyright (c) 2013 Werner Mayer <wmayer[at]users.sourceforge.net>     *
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

#ifndef APLANGUI_ACTIVEANALYSISOBSERVER_HPP
#define APLANGUI_ACTIVEANALYSISOBSERVER_HPP

#include <App/DocumentObserver.h>
#include <Gui/Tree.h>

namespace Gui
{
    class Document;
    class ViewProviderDocumentObject;
}

namespace Aplan
{
    class AplanAnalysis;
}

namespace AplanGui
{
    class ActiveAnalysisObserver : public App::DocumentObserver
    {
    public:
        static ActiveAnalysisObserver *instance();

        void setActiveObject(Aplan::AplanAnalysis *);
        Aplan::AplanAnalysis *getActiveObject() const;
        bool hasActiveObject() const;
        void highlightActiveObject(const Gui::HighlightMode &, bool);
        void unsetActiveObject();

    private:
        ActiveAnalysisObserver();
        ~ActiveAnalysisObserver();

        void slotDeletedDocument(const App::Document &Doc);
        void slotDeletedObject(const App::DocumentObject &Obj);

    private:
        static ActiveAnalysisObserver *inst;
        Aplan::AplanAnalysis *activeObject;
        Gui::ViewProviderDocumentObject *activeView;
        Gui::Document *activeDocument;
        Gui::HighlightMode highlightMode;
    };
} // namespace AplanGui

#endif // APLANGUI_ACTIVEANALYSISOBSERVER_HPP
