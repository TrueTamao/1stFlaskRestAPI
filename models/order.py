import os
import stripe
from db import db
from typing import List


class ItemInOrder(db.Model):
    __tablename__ ="itemInOrder"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    quantity = db.Column(db.Integer)
    
    item = db.relationship("ItemModel")
    order = db.relationship("OrderModel", back_populates="items")

class OrderModel(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)
    items = db.relationship("ItemInOrder", back_populates="order")
    
    @property
    def description(self) -> str:
        """
        Generates a simple string representing this order, in the format of "5x chair, 2x table"
        """
        item_count = [f"{item_data.quantity} x {item_data.item.name}" for item_data in self.items]
        return ",".join(item_count)

    @property
    def amount(self) -> int:
        """
        Calculates the total amount to charge for this order.
        Assumes item price is in USD–multi-currency becomes much tricker!
        :return int: total amount of cents to be charged in this order.x`
        """
        return int(sum(item_data.item.price * item_data.quantity for item_data in self.items) * 100)

    @classmethod
    def find_all(cls) -> List["OrderModel"]:
        return cls.query.all()

    @classmethod
    def find_by_id(cls, id: int) -> "OrderModel":
        return cls.query.filter_by(id=id).first()
    
    def set_status(self, new_status: str) -> None:
        self.status = new_status
        self.save_to_db()
    
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self) -> None:
        db.session.remove(self)
        db.session.commit()

    def charge_with_stripe(self, token: str) -> stripe.Charge:
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        return stripe.Charge.create(
            amount=self.amount,  # amount of cents (100 means USD$1.00)
            currency=CURRENCY,
            description=self.description,
            source=token
        )


