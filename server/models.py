# server/models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, CheckConstraint
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

# naming convention helps Alembic generate consistent FKs
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # has many RestaurantPizza
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # avoid recursive serialization: don't serialize back ref from RP to restaurant
    serialize_rules = ("-restaurant_pizzas.restaurant",)

    def __repr__(self):
        return f"<Restaurant {self.id} {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # pizzas have many RestaurantPizza
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    serialize_rules = ("-restaurant_pizzas.pizza",)

    def __repr__(self):
        return f"<Pizza {self.id} {self.name}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False
    )
    pizza_id = db.Column(
        db.Integer, db.ForeignKey("pizzas.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    # avoid recursion when serializing
    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")

    # also add a DB-level check if you want (optional)
    __table_args__ = (
        CheckConstraint("price >= 1 AND price <= 30", name="price_between_1_and_30"),
    )

    @validates("price")
    def validate_price(self, key, value):
        if value is None:
            raise ValueError("price must be present")
        try:
            v = int(value)
        except Exception:
            raise ValueError("price must be an integer")
        if v < 1 or v > 30:
            raise ValueError("price must be between 1 and 30")
        return v

    def __repr__(self):
        return f"<RestaurantPizza {self.id} price={self.price}>"
