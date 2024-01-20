import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    try:
        name = request.args.get("name")
        map_url = request.args.get("map_url")
        img_url = request.args.get("img_url")
        location = request.args.get("location")
        has_sockets = bool(request.args.get("has_sockets"))
        has_toilet = bool(request.args.get("has_toilet"))
        has_wifi = bool(request.args.get("has_wifi"))
        can_take_calls = bool(request.args.get("can_take_calls"))
        seats = request.args.get("seats")
        coffee_price = request.args.get("coffee_price")

        # Check for existing cafe with the same name
        existing_cafe = Cafe.query.filter_by(name=name.strip()).first()
        if existing_cafe:
            return jsonify({"error": {"message": "Cafe with this name already exists"}}), 400

        # Continue with the insertion
        new_cafe = Cafe(
            name=name,
            map_url=map_url,
            img_url=img_url,
            location=location,
            has_sockets=has_sockets,
            has_toilet=has_toilet,
            has_wifi=has_wifi,
            can_take_calls=can_take_calls,
            seats=seats,
            coffee_price=coffee_price
        )

        db.session.add(new_cafe)
        db.session.commit()

        success = {"response": {"success": "Successfully added new data"}}
        return jsonify(success)

    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>', methods=['PATCH', 'PUT'])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    cafe = next((c for c in cafes if c.id == cafe_id), None)
    if cafe is None:
        return jsonify({'error': 'Cafe not found'}), 404
    elif new_price is None or new_price == '':
        return jsonify({'error': 'Price not provided'}), 400
    else:
        cafe.coffee_price = new_price
        db.session.commit()
    return jsonify({'message': f'Price for Cafe {cafe_id} updated successfully', 'new_price': new_price})


@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)

    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()

    cafes_data = [data.to_dict() for data in all_cafes]
    return jsonify(cafes=cafes_data)


@app.route("/search")
def search_cafes():
    location_param = request.args.get('loc')
    if location_param:
        result = db.session.execute(db.select(Cafe).where(Cafe.location == location_param))
        cafes_in_location = result.scalars().all()

        if cafes_in_location:
            cafes_data = [data.to_dict() for data in cafes_in_location]
            return jsonify(cafes=cafes_data)
        else:
            return jsonify(error={"Not Found": f"Sorry we don't have coffee at location: {location_param}"}), 404
    else:
        return jsonify(error={"Bad Request": "Location parameter (loc) is required"}), 400


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")

    if api_key == "3d6f45a5fc12445dbac2f59c3b6c7cb1":
        cafe_to_close = db.session.query(Cafe).get(cafe_id)
        if cafe_to_close:
            db.session.delete(cafe_to_close)
            db.session.commit()
            return jsonify(response={"success": "Cafe successfully deleted."}), 200
        else:
            return jsonify(error={"error": "Cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Incorrect API key."}), 403


if __name__ == '__main__':
    app.run(debug=True)