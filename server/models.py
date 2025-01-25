from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Define metadata with naming convention
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize SQLAlchemy with metadata
db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"  # Fixed typo from _tablename_

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationships
    restaurant_pizzas = relationship("RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan")
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    # Serialization rules
    serialize_rules = ("-restaurant_pizzas", "-pizzas")

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"  # Fixed typo from _tablename_ to __tablename__

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Relationships
    restaurant_pizzas = relationship("RestaurantPizza", back_populates="pizza", cascade="all, delete-orphan")
    restaurants = association_proxy("restaurant_pizzas", "restaurant")

    # Serialization rules
    serialize_rules = ("-restaurant_pizzas", "-restaurants")

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"  # Fixed typo from _tablename_

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign keys
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)  # Ensure the target table 'pizzas' is correct
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)

    # Relationships
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")
    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")

    # Serialization rules
    serialize_rules = ("-pizza.restaurant_pizzas", "-restaurant.restaurant_pizzas")

    # Validation
    @validates("price")
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"

