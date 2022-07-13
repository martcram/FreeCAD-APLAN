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

__title__ = "FreeCAD APLAN Flask web app"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

import FreeCAD
try:
    import flask
    import flask_caching
    import json
    import typing
except ImportError as ie:
    print("Missing dependency! Please install the following Python module: {}".format(str(ie.name or "")))


staticDir:    typing.Final[str] = FreeCAD.getHomePath() + "Mod/Aplan/aplanwebapp/static/"
templatesDir: typing.Final[str] = FreeCAD.getHomePath() + "Mod/Aplan/aplanwebapp/templates/"


config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = flask.Flask(__name__, template_folder = templatesDir)
app.config.from_mapping(config)
cache = flask_caching.Cache(app)


# ********************* General *********************
@app.errorhandler(404)
def error_404(error: Exception) -> flask.typing.ResponseReturnValue:
    return flask.render_template("error_404.html"), 404


@app.errorhandler(500)
def error_500(error: Exception) -> flask.typing.ResponseReturnValue:
    return flask.render_template("error_500.html"), 500


@app.route("/aplan/config_params")
def getConfigParams():
    with open(staticDir + "json/config_params.json", "r") as read_file:
        message = json.load(read_file)
    return flask.jsonify(message)


@app.route("/aplan/animations", methods=["GET", "POST"])
def toggleAnimations():
    if flask.request.method == "GET":
        return flask.jsonify(cache.get("animations"))
    elif flask.request.method == "POST":
        args: typing.Dict[str, str] = flask.request.args.to_dict()
        cache.set("animations", {"enabled": args["enable"]})
        return "Success", 200


# ********************* Connection graph *********************
connectionGraphCachedParams = [
    "animations",
    "cg_file_location",
    "cg_graph",
    "cg_selected_connections"
]


@app.route("/aplan/connection_graph/clear_cache", methods=["POST"])
def clearCacheConnectionGraph():
    param: str
    for param in connectionGraphCachedParams:
        cache.delete(param)
    return "Success", 200


@app.route("/aplan/connection_graph/js", methods=["GET", "POST"])
def connectionGraphJS():
    if flask.request.method == "GET":
        try:
            args: typing.Dict[str, str] = flask.request.args.to_dict()
            with open(args.get("fileLoc", ""), "r") as read_file:
                data = json.load(read_file)
            cache.set("cg_graph", data)
            return flask.jsonify(data)
        except Exception as e:
            return flask.jsonify({"nodes": [], "links": []})
    elif flask.request.method == "POST":
        cache.set("cg_graph", flask.request.get_json())
        return "Success", 200


@app.route("/aplan/connection_graph/json")
def getConnectionGraphJSON():
    return flask.jsonify(cache.get("cg_graph"))


@app.route("/aplan/connection_graph/selected_connections", methods=["GET", "POST"])
def getSelectedConnections():
    if flask.request.method == "GET":
        return flask.jsonify(cache.get("cg_selected_connections"))
    elif flask.request.method == "POST":
        cache.set("cg_selected_connections", flask.request.get_json())
        return "Success", 200


@app.route("/aplan/connection_graph")
def renderConnectionGraph():
    args: typing.Dict[str, str] = flask.request.args.to_dict()
    cache.set("cg_file_location", args.get("fileLoc", ""))
    return flask.render_template("connection_graph.html", fileLocation=cache.get("cg_file_location"))


# ********************* Obstruction graph *********************
obstructionGraphCachedParams = [
    "animations",
    "og_file_location",
    "og_graph",
    "og_selected_obstructions"
]


@app.route("/aplan/obstruction_graph/clear_cache", methods=["POST"])
def clearCacheObstructionGraph():
    param: str
    for param in obstructionGraphCachedParams:
        cache.delete(param)
    return "Success", 200


@app.route("/aplan/obstruction_graph/js", methods=["GET", "POST"])
def obstructionGraphJS():
    if flask.request.method == "GET":
        try:
            args: typing.Dict[str, str] = flask.request.args.to_dict()
            with open(args.get("fileLoc", ""), "r") as read_file:
                data = json.load(read_file)
            cache.set("og_graph", data)
            return flask.jsonify(data)
        except Exception as e:
            return flask.jsonify({"nodes": [], "links": []})
    elif flask.request.method == "POST":
        cache.set("og_graph", flask.request.get_json())
        return "Success", 200


@app.route("/aplan/obstruction_graph/json")
def getObstructionGraphJSON():
    return flask.jsonify(cache.get("og_graph"))


@app.route("/aplan/obstruction_graph/selected_obstructions", methods=["GET", "POST"])
def getSelectedObstructions():
    if flask.request.method == "GET":
        return flask.jsonify(cache.get("og_selected_obstructions"))
    elif flask.request.method == "POST":
        cache.set("og_selected_obstructions", flask.request.get_json())
        return "Success", 200


@app.route("/aplan/obstruction_graph")
def renderObstructionGraph():
    args: typing.Dict[str, str] = flask.request.args.to_dict()
    cache.set("og_file_location", args.get("fileLoc", ""))
    return flask.render_template("obstruction_graph.html", fileLocation=cache.get("og_file_location"))
