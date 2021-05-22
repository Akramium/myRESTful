from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from sqlite3 import IntegrityError

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
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
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route('/random')
def random_cafe():
    # fetch all cafes
    all_cafes = db.session.query(Cafe).all()
    # get a random cafe
    cafe = random.choice(all_cafes)
    return jsonify(cafe=cafe.to_dict())


@app.route('/all')
def all():
    # fetch all cafes
    all_cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route('/search')
def search():
    loc = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=loc).all()
    print(len(cafes))
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={
            "Not Found": "Sorry we don't have a cafe at that location."
        })


@app.route('/add', methods=['POST'])
def add():
    pre_create_cafe = Cafe(
        name=request.args.get("name"),
        map_url=request.args.get("map_url"),
        img_url=request.args.get("img_url"),
        location=request.args.get("location"),
        seats=request.args.get("seats"),
        has_toilet=bool(request.args.get("has_toilet")),
        has_wifi=bool(request.args.get("has_wifi")),
        has_sockets=bool(request.args.get("has_sockets")),
        can_take_calls=bool(request.args.get("can_take_calls")),
        coffee_price=request.args.get("coffee_price"),
    )
    db.session.add(pre_create_cafe)
    db.session.commit()
    return jsonify(response={
        "success": "Successfully added the new cafe."
    })


## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

@app.route('/update-price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(success="You successfully updated the price")
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


## HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete(cafe_id):
    api_key = request.args.get("api_key")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        if api_key == "TopSecretAPIKey":
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success="You successfully deleted the coffee")
        else:
            return jsonify(error="Sorry that's not allowed, Make Sure Your API Key is correct!")
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


if __name__ == '__main__':
    app.run(debug=True)
