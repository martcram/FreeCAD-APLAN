from aplantools import aplanutils
try:
    import flask
    import flask_caching
    import FreeCAD
    import typing
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


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


@app.errorhandler(404)
def error_404(error: Exception) -> flask.typing.ResponseReturnValue:
    return flask.render_template("error_404.html"), 404


@app.errorhandler(500)
def error_500(error: Exception) -> flask.typing.ResponseReturnValue:
    return flask.render_template("error_500.html"), 500
