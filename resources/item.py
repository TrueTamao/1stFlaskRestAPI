from flask_restful import Resource
from flask_jwt_extended import fresh_jwt_required, jwt_required
from flask import request

from models.item import ItemModel
from schemas.item import ItemSchema
from libs.strings import gettext

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)

class Item(Resource):
    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if(item):
             return item_schema.dump(item), 200
        
        return {"message:", gettext("item_not_found")}, 404
    
    @classmethod
    @fresh_jwt_required
    def post(cls, name:str):
        item = ItemModel.find_by_name(name)
        if(item):
            return {"message:", gettext("item_name_exists").format(name)}, 404

        item_json = request.get_json()
        item_json["name"] = name

        item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except:
            return {"messsage:", gettext("item_error_inserting")}, 500
        
        return item_schema.dump(item), 201
        
    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if(item):
            item.remove_from_db()
            return {"message:", gettext("item_deleted")}, 201
        
        return {"message:", gettext("item_not_found")}, 404
    
    @classmethod
    @fresh_jwt_required
    def put(cls, name:str):
        item = ItemModel.find_by_name(name)
        item_json = request.get_json()

        if(item):
            item.price = item_json["price"]
        else:
            item_json["name"] = name
            item = item_schema.load(item_json)

        item.save_to_db()

        return item_schema.dump(item), 201


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": item_schema.dump( ItemModel.find_all(), many=True)}, 200