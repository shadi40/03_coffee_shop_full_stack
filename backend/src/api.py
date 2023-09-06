import os
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#with app.app_context():
#    db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    data = request.get_json()
    try:
        new_drink = Drink(title=data['title'], recipe=json.dumps(data['recipe']))
        new_drink.insert()
        return jsonify({
            "success": True,
            "drinks": [new_drink.long()]
        })
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    
    data = request.get_json()
    try:
        if 'title' in data:
            drink.title = data['title']
        if 'recipe' in data:
            drink.recipe = json.dumps(data['recipe'])
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        })
    except:
        abort(422)

# Error Handling

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(AuthError)
def handle_auth_error(exception):
    return jsonify({
        "success": False,
        "error": exception.status_code,
        "message": exception.error['description']
    }), exception.status_code

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

if __name__ == "__main__":
    app.debug = True
    app.run()
