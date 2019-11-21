from ma import ma

from models.order import OrderModel, ItemInOrder
from schemas.item import ItemSchema

class ItemInOrderSchema(ma.ModelSchema):
    class Meta:
        model = ItemInOrder
        include_fk = True
    item = ma.Nested(ItemSchema)

class OrderSchema(ma.ModelSchema):
    class Meta:
        model = OrderModel
        load_only = ("token",)
        dump_only = ("id", "status",)
        include_fk = True
    items = ma.Nested(ItemInOrderSchema, many=True)