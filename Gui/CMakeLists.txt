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
)

if (BUILD_QT5)
    qt5_add_resources(AplanResource_SRCS Resources/Aplan.qrc)
else()
    qt4_add_resources(AplanResource_SRCS Resources/Aplan.qrc)
endif()
SOURCE_GROUP("Resources" FILES ${AplanResource_SRCS})

SET(AplanGui_SRCS_ViewProvider
    ViewProviderAnalysis.cpp
    ViewProviderAnalysis.hpp
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
    ${AplanGui_SRCS_ViewProvider}
    ${AplanGui_SRCS_Module}
)

SET(AplanGuiIcon_SVG
    Resources/icons/APLAN_Workbench.svg
)

add_library(AplanGui SHARED ${AplanGui_SRCS} ${AplanGuiIcon_SVG})
target_link_libraries(AplanGui ${AplanGui_LIBS})
    
fc_copy_sources(AplanGui "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_DATADIR}/Mod/Aplan" ${AplanGuiIcon_SVG})

INSTALL(FILES ${AplanGuiIcon_SVG} DESTINATION "${CMAKE_INSTALL_DATADIR}/Mod/Aplan/Resources/icons")


SET_BIN_DIR(AplanGui AplanGui /Mod/Aplan)
SET_PYTHON_PREFIX_SUFFIX(AplanGui)


INSTALL(TARGETS AplanGui DESTINATION ${CMAKE_INSTALL_LIBDIR})
