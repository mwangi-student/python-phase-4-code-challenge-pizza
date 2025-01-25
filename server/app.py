#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Corrected _file_ to __file__
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)  # Corrected _name_ to __name__
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200


@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  # Updated to use db.session.get
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify({
        **restaurant.to_dict(),
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza": rp.pizza.to_dict()
            } for rp in restaurant.restaurant_pizzas
        ]
    }), 200


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  # Updated to use db.session.get
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return '', 204


@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas]), 200


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        # Ensure price validation is consistent with requirements
        if not (1 <= data['price'] <= 30):
            raise ValueError("validation errors")  # Aligned with test expectation

        restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        return jsonify({
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza_id": restaurant_pizza.pizza_id,  # Added to match test expectations
            "restaurant_id": restaurant_pizza.restaurant_id,  # Added to match test expectations
            "pizza": restaurant_pizza.pizza.to_dict(),
            "restaurant": restaurant_pizza.restaurant.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400



@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":  # Corrected _name_ to __name__
    app.run(port=5555, debug=True)
