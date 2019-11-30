from flask import Flask, Blueprint
from app import models
from app import users
import views
import pymongo


# client = pymongo.MongoClient("mongodb+srv://DineshS31:sd8122528458%40@cluster0-tn79l.mongodb.net/ecommerce_internal?retryWrites=false&w=majority",connectTimeoutMS=300000,maxPoolSize=50)
connection = pymongo.MongoClient("mongodb://ds251158.mlab.com", 51158, retryWrites=False)
db = connection.ecommerce_internal
db.authenticate("Dinesh", "s8122528458")

app = Flask(__name__)

app.register_blueprint(views.app)
app.register_blueprint(users.users)
