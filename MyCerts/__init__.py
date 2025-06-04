from flask import Blueprint

mycerts = Blueprint('mycerts', __name__)

from . import routes 