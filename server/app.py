# server/app.py
from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()
migrate = Migrate(app, db)

# --- ROUTES ---

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    out = [{"id": r.id, "name": r.name, "address": r.address} for r in restaurants]
    return make_response(jsonify(out), 200)


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    r = Restaurant.query.get(id)
    if not r:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    rp_list = []
    for rp in r.restaurant_pizzas:
        rp_list.append({
            "id": rp.id,
            "pizza": {
                "id": rp.pizza.id,
                "ingredients": rp.pizza.ingredients,
                "name": rp.pizza.name
            },
            "pizza_id": rp.pizza_id,
            "price": rp.price,
            "restaurant_id": rp.restaurant_id
        })

    resp = {
        "id": r.id,
        "name": r.name,
        "address": r.address,
        "restaurant_pizzas": rp_list
    }
    return make_response(jsonify(resp), 200)


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    r = Restaurant.query.get(id)
    if not r:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    db.session.delete(r)
    db.session.commit()
    return make_response("", 204)


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    out = [{"id": p.id, "ingredients": p.ingredients, "name": p.name} for p in pizzas]
    return make_response(jsonify(out), 200)


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        new_rp = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(new_rp)
        db.session.commit()

        return jsonify(new_rp.to_dict()), 201

    except (ValueError, KeyError):
        return jsonify({"errors": ["validation errors"]}), 400



if __name__ == "__main__":
    app.run(port=5555, debug=True)
