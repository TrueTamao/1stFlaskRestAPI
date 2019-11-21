from flask_restful import Resource
from collections import Counter
from flask import request


from models.order import OrderModel, ItemInOrder
from models.item import ItemModel
from schemas.order import OrderSchema


order_schema = OrderSchema()

class Order(Resource):
    @classmethod
    def get(cls):
        all_order = OrderModel.find_all()
        return order_schema.dump(all_order, many=True), 200

    @classmethod
    def post(cls):
        """
        Expect a token and a list of item ids from the request body.
        Construct an order and talk to the Strip API to make a charge.
        """
        data = request.get_json()  # token + list of item ids  [1, 2, 3, 5, 5, 5]
        items = []
        item_id_quantities = Counter(data["item_ids"])

        # Iterate over items and retrieve them from the database
        for _id, _count in item_id_quantities.most_common():
            item = ItemModel.find_by_id(_id)
            if not item:
                return {"message": gettext("order_item_by_id_not_found").format(_id)}, 404
            
            items.append(ItemInOrder(item_id=_id, quantity=_count))
        
        order = OrderModel(items = items, status="pending")
        order.save_to_db()

        order.set_status("failed")  # assume the order would fail until it's completed
        #order.charge_with_stripe(data["token"])
        order.set_status("complete")  # charge succeeded

        return order_schema.dump(order), 200
