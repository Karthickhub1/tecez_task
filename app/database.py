from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)

db = client["erp_db"]


customers_collection = db["customers"]
products_collection = db["products"]
orders_collection = db["sales_orders"]