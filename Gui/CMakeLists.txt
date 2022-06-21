include_directories(
    ${CMAKE_BINARY_DIR}
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_CURRENT_BINARY_DIR}
    ${Boost_INCLUDE_DIRS}
    ${COIN3D_INCLUDE_DIRS}
    ${ZLIB_INCLUDE_DIR}
    ${OCC_INCLUDE_DIR}
    ${PYTHON_INCLUDE_DIRS}
)

link_directories(${OCC_LIBRARY_DIR})

set(AplanGui_LIBS
    Aplan
    FreeCADGui
    PartGui
)

set(AplanGui_MOC_HDRS
    TaskAplanAnalysis.hpp
)
fc_wrap_cpp(AplanGui_MOC_SRCS ${AplanGui_MOC_HDRS})
SOURCE_GROUP("Moc" FILES ${AplanGui_MOC_SRCS})

SET(AplanGui_UIC_SRCS
    TaskAplanAnalysis.ui
)
if(BUILD_QT5)
    qt5_wrap_ui(AplanGui_UIC_HDRS ${AplanGui_UIC_SRCS})
else()
    qt4_wrap_ui(AplanGui_UIC_HDRS ${AplanGui_UIC_SRCS})
endif()

SET(AplanGui_DLG_SRCS
    ${AplanGui_UIC_HDRS}
    TaskAplanAnalysis.ui
    TaskAplanAnalysis.cpp
    TaskAplanAnalysis.hpp
)
SOURCE_GROUP("Dialogs" FILES ${AplanGui_DLG_SRCS})
 
if (BUILD_QT5)
    qt5_add_resources(AplanResource_SRCS Resources/Aplan.qrc)
else()
    qt4_add_resources(AplanResource_SRCS Resources/Aplan.qrc)
endif()
SOURCE_GROUP("Resources" FILES ${AplanResource_SRCS})

SET(AplanGui_SRCS_ViewProvider
    ViewProviderAnalysis.cpp
    ViewProviderAnalysis.hpp
    ViewProviderCompound.cpp
    ViewProviderCompound.hpp
    ViewProviderPartFilter.cpp
    ViewProviderPartFilter.hpp
)
SOURCE_GROUP("ViewProvider" FILES ${AplanGui_SRCS_ViewProvider})

SET(AplanGui_SRCS_Module
    ActiveAnalysisObserver.cpp
    ActiveAnalysisObserver.hpp
    AppAplanGui.cpp
    AppAplanGuiPy.cpp
    Command.cpp
    Resources/Aplan.qrc
    PreCompiled.cpp
    PreCompiled.hpp
    Workbench.cpp
    Workbench.hpp
)
SOURCE_GROUP("Module" FILES ${AplanGui_SRCS_Module})

SET(AplanGui_SRCS
    ${AplanResource_SRCS}
    ${AplanGui_SRCS_Module}
    ${AplanGui_SRCS_ViewProvider}
    ${AplanGui_DLG_SRCS}
)

SET(AplanGuiIcon_SVG
    Resources/icons/APLAN_Workbench.svg
)

add_library(AplanGui SHARED ${AplanGui_SRCS} ${AplanGuiIcon_SVG})
target_link_libraries(AplanGui ${AplanGui_LIBS})
    
fc_copy_sources(AplanGui "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_DATADIR}/Mod/Aplan" ${AplanGuiIcon_SVG})

INSTALL(FILES ${AplanGuiIcon_SVG} DESTINATION "${CMAKE_INSTALL_DATADIR}/Mod/Aplan/Resources/icons")


# Python modules ui files, they are copied as they are, thus need not to be added to Aplan.qrc
# see https://forum.freecadweb.org/viewtopic.php?f=10&t=25833
SET(AplanGuiPythonUI_SRCS
    Resources/ui/ExcludeParts.ui
    Resources/ui/GroupParts.ui
)

ADD_CUSTOM_TARGET(AplanPythonUi ALL
    SOURCES ${AplanGuiPythonUI_SRCS}
)

fc_copy_sources(AplanPythonUi "${CMAKE_BINARY_DIR}/Mod/Aplan" ${AplanGuiPythonUI_SRCS})

INSTALL(FILES ${AplanGuiPythonUI_SRCS} DESTINATION Mod/Aplan/Resources/ui)


SET_BIN_DIR(AplanGui AplanGui /Mod/Aplan)
SET_PYTHON_PREFIX_SUFFIX(AplanGui)


INSTALL(TARGETS AplanGui DESTINATION ${CMAKE_INSTALL_LIBDIR})
