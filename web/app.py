from flask import Flask, jsonify, request
from flask_restful import Api, Resource
#from flask_pymongo import PyMongo
from pymongo import MongoClient
import bcrypt


app = Flask(__name__)
api = Api(app)

#app.config["MONGO_URI"] = "mongodb://localhost:27017/sentencesDatabase"
#mongo = PyMongo(app)
client = MongoClient("mongodb://db:27017")
db = client.sentencesDatabase
users = db["Users"]



class Register(Resource):
    def post(self):
        #Get user posted data
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        #hash the password
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #saved the posted data

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens": 6
        })

        returnData = {
                "Status Code" : 200,
                "Message": "You successfully signed up for our API" ,
        }
        return jsonify(returnData)


       
def verifyPw(username, password):
    hashed_pw= users.find({
            "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
        "Username":username
    })[0]["Tokens"]
    return tokens


class StoreSentence(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        #Verify user name pasword and Token
        correct_pw = verifyPw(username, password)

        # if not correct_pw:
        #     retJson = {
        #         "Status Code": 302,
        #         "Message" : "Incorrect password or Username"
        #     }
        #     return jsonify(retJson)

        if not correct_pw:
            retJson = {
                "Status Code": 301,
                "Message": "Password or Username incorrect"
            }
            return jsonify(retJson)

        numberOfTokens = countTokens(username)
        if numberOfTokens <= 0:
            retJson = {
                "Status Code" : 301,
                "Message" : "Out of tokens"
            }
            return jsonify(retJson)

# Store the sentence and take away one token from his tokens

        users.update({
            "Username": username
            },
         {
            "$set":{
                        "Sentence": sentence,
                        "Tokens": numberOfTokens - 1
                    }
         })

        retJson = {
            "Status Code": 200,
            "Message": "sentence saved successfully and one token deducted from your tokens"
        }
        return jsonify(retJson)


class RetriveSentence(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]

        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
                "Status Code" : 301,
                "Messaege" : "Password or user name incorrect"
            }
            return jsonify(retJson)
        

        numberOfTokens = countTokens(username)

        if numberOfTokens <=0:
            retJson={
                "Status Code": 301,
                "Message": "Not enough token"
            }
            return jsonify(retJson)
        
        users.update({
            "Username": username
        },{
            "$set":{
                "Tokens": numberOfTokens-1
            }
        })

        sentence = users.find({
                "Username":username
        })[0]["Sentence"]

        retJson = {
            "Status Code": 200,
            "Message": sentence
        }
        return jsonify(retJson)




api.add_resource(Register, '/register')
api.add_resource(StoreSentence, '/store')
api.add_resource(RetriveSentence, '/retrive')


if __name__ == "__main__":
    app.run(host='0.0.0.0')

