import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()


#--------------------------------------------------------------
#GET Endpoints
#--------------------------------------------------------------

@app.route("/drinks")
def get_drinks():
    drinks = Drink.query.all()
    Formated_Drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success":True,
        "drinks":Formated_Drinks
    })
  
@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_details(payload):
    drinks = Drink.query.all()
    Formated_Drinks = [drink.long() for drink in drinks]
    return jsonify({
        "success":True,
        "drinks":Formated_Drinks
    })

#--------------------------------------------------------------
#POST Endpoint
#--------------------------------------------------------------

@app.route("/drinks",methods=['POST'])
@requires_auth("post:drinks")
def add_drink(payload):
    body = request.get_json()
    if body is None:
        abort(400)
    title = body['title']
    recipe = body['recipe']
    try:
        drink = Drink(title=title,recipe=json.dumps(recipe))
        drink.insert()
        temp_list = [drink.long()]
        return jsonify({
            "success":True,
            "drink":temp_list
        })
    except:
        abort(422)    

#--------------------------------------------------------------
#PATCH Endpoint
#--------------------------------------------------------------

@app.route("/drinks/<int:id>",methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(payload,id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    body = request.get_json()
    title = body.get("title",drink.title)
    recipe = body.get("recipe",drink.recipe)
    try:
        drink.title=title
        drink.recipe=json.dumps(recipe)
        drink.update()
        temp_list =[drink.long()]
        return jsonify({
            "success":True,
            "drinks":temp_list
        })
    except:
        abort(422)    

#--------------------------------------------------------------
#Delete Endpoint
#--------------------------------------------------------------

@app.route("/drinks/<int:id>",methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(payload,id):
   drink = Drink.query.get(id)
   if drink is None:
       abort(404)

   try:
       drink.delete()
       return jsonify({
           "success":True,
           "delete":id
       })   
   except:
        abort(422)   
   
#--------------------------------------------------------------
#Error handlers
#--------------------------------------------------------------

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success":False,
                    "error":400,
                    "message":"bad request"
                    }),400

@app.errorhandler(AuthError)
def auth_errors(auth):
    return jsonify({
        "success":False,
        "error":auth.status_code,
        "message":auth.error['code']
    }),auth.status_code
   