/******************************************************************************
 *                                                                            *
 *   Copyright (c) 2013 Jan Rheinländer <jrheinlaender@users.sourceforge.net> *
 *   Copyright (c) 2022 Martijn Cramer <martijn.cramer@outlook.com>           *
 *                                                                            *
 *   This file is part of the FreeCAD CAx development system.                 *
 *                                                                            *
 *   This library is free software; you can redistribute it and/or            *
 *   modify it under the terms of the GNU Library General Public              *
 *   License as published by the Free Software Foundation; either             *
 *   version 2 of the License, or (at your option) any later version.         *
 *                                                                            *
 *   This library  is distributed in the hope that it will be useful,         *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of           *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            *
 *   GNU Library General Public License for more details.                     *
 *                                                                            *
 *   You should have received a copy of the GNU Library General Public        *
 *   License along with this library; see the file COPYING.LIB. If not,       *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,            *
 *   Suite 330, Boston, MA  02111-1307, USA                                   *
 *                                                                            *
 ******************************************************************************/

#ifndef TASKAPLANANALYSIS_HPP
#define TASKAPLANANALYSIS_HPP

#include <string>

#include <Gui/Selection.h>
#include <Gui/TaskView/TaskView.h>
#include <Gui/TaskView/TaskDialog.h>

#include <Mod/Aplan/App/AplanAnalysis.hpp>
#include <Mod/Aplan/Gui/ViewProviderAnalysis.hpp>

#include <QObject>

class Ui_TaskAplanAnalysis;

namespace AplanGui
{

    class TaskAplanAnalysis : public Gui::TaskView::TaskBox
    {
        Q_OBJECT

    public:
        TaskAplanAnalysis(ViewProviderAplanAnalysis *analysisView, const char* pixmapname = "", QWidget *parent = 0);
        ~TaskAplanAnalysis();

        const std::string getWorkingDirectory() const;
        void setWorkingDirectory(const std::string &path);
        const std::string getAnalysisLabel() const;
        void setAnalysisLabel(const std::string &label);

    private Q_SLOTS:
        void chooseWorkingDir();

    private:
        Ui_TaskAplanAnalysis *ui;
        std::string workingDir;

    protected:
        QWidget *proxy;
        ViewProviderAplanAnalysis *analysisView;
    };

    class TaskDlgAplanAnalysis : public Gui::TaskView::TaskDialog
    {
        Q_OBJECT

    public:
        TaskDlgAplanAnalysis(ViewProviderAplanAnalysis *analysisView);

        // is called by the framework when the dialog is opened
        void open();

        // is called by the framework if the dialog is accepted (Ok)
        bool accept();

        // is called by the framework if the dialog is rejected (Cancel)
        bool reject();

        // returns Close and Help buttons
        virtual QDialogButtonBox::StandardButtons getStandardButtons(void) const
        {
            return QDialogButtonBox::Ok | QDialogButtonBox::Cancel;
        }

        ViewProviderAplanAnalysis* getAnalysisView() const
        {
            return this->analysisView;
        }

    protected:
        Aplan::AplanAnalysis *analysis;
        ViewProviderAplanAnalysis *analysisView;
        TaskAplanAnalysis *parameter;
    };

} // namespace AplanGui

#endif // TASKAPLANANALYSIS_HPP
