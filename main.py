from fastapi import FastAPI
import json

app = FastAPI(title="USANA Nutritional Coach API")

def load_products():
    with open("products.json", "r") as file:
        return json.load(file)

@app.get("/")
def home():
    return {"message": "Welcome to the USANA Nutritional Coach API!"}

@app.get("/products")
def get_products():
    return {"catalog": load_products()}