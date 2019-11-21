from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import marshmallow as mallow

from db import db
from ma import ma
from blacklist import BLACKLIST
from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.store import Store, StoreList
from resources.item import Item, ItemList
from resources.order import Order


app = Flask(__name__)
load_dotenv(".env")
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
api = Api(app)
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(mallow.ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


jwt = JWTManager(app)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Order, "/order")

if __name__ == "__main__":
    ma.init_app(app)
    app.run(port=5000, debug=True)