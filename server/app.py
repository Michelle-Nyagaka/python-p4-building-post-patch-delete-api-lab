from flask import Flask, request, make_response
from models import db, Bakery, BakedGood
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return "Welcome to the Bakery API!"

# GET ROUTES 
@app.route('/bakeries')
def get_bakeries():
    bakeries = [bakery.to_dict(rules=('-baked_goods.bakery',)) for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response({"message": "Bakery not found"}, 404)

    if request.method == 'GET':
        return make_response(bakery.to_dict(), 200)

    elif request.method == 'PATCH':
        # Update only the fields sent in the form
        for attr in request.form:
            setattr(bakery, attr, request.form.get(attr))

        db.session.add(bakery)
        db.session.commit()
        return make_response(bakery.to_dict(), 200)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    return make_response([g.to_dict(rules=('-bakery.baked_goods',)) for g in goods], 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    good = BakedGood.query.order_by(BakedGood.price.desc()).first()
    return make_response(good.to_dict(rules=('-bakery.baked_goods',)), 200)

# POST ROUTES
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    new_good = BakedGood(
        name=request.form.get("name"),
        price=request.form.get("price"),
        bakery_id=request.form.get("bakery_id")
    )
    db.session.add(new_good)
    db.session.commit()
    return make_response(new_good.to_dict(), 201)

# DELETE ROUTES 
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    good = BakedGood.query.get(id)
    if not good:
        return make_response({"message": "Baked good not found"}, 404)

    db.session.delete(good)
    db.session.commit()
    return make_response({
        "delete_successful": True,
        "message": f"{good.name} was deleted."
    }, 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
