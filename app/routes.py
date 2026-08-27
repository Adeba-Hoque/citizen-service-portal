from flask import Blueprint

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return "Citizen Service Request Portal is running!"