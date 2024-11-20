from flask import Flask, request, jsonify
from uuid import uuid4
import re

app = Flask(__name__)


receipts = {}


class Item:
    def __init__(self, shortDescription, price):
        self.shortDescription = shortDescription
        self.price = price
    
    def validate(self):
        if not re.match(r'^[\w\s\-]+$', self.shortDescription):
            raise ValueError("Invalid shortDescription format")
        if not re.match(r'^\d+\.\d{2}$', self.price):
            raise ValueError("Invalid price format")
        return True

class Receipt:
    def __init__(self, retailer, purchaseDate, purchaseTime, items, total):
        self.retailer = retailer
        self.purchaseDate = purchaseDate
        self.purchaseTime = purchaseTime
        self.items = [Item(**item) for item in items]
        self.total = total
    
    def validate(self):
        if not re.match(r'^[\w\s\-\&]+$', self.retailer):
            raise ValueError("Invalid retailer format")
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', self.purchaseDate):
            raise ValueError("Invalid purchaseDate format")
        if not re.match(r'^\d{2}:\d{2}$', self.purchaseTime):
            raise ValueError("Invalid purchaseTime format")
        if not re.match(r'^\d+\.\d{2}$', self.total):
            raise ValueError("Invalid total format")
        for item in self.items:
            item.validate()
        return True


def calculate_points(receipt):
    total = float(receipt.total)
    if total < 10:
        return 50
    elif total < 50:
        return 100
    else:
        return 200

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    data = request.get_json()

    try:
        receipt = Receipt(**data)
        receipt.validate()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    # Generate a unique receipt ID and store the receipt
    receipt_id = str(uuid4())
    receipts[receipt_id] = receipt
    
    return jsonify({"id": receipt_id}), 200

@app.route('/receipts/<id>/points', methods=['GET'])
def get_receipt_points(id):
    if id not in receipts:
        return jsonify({"error": "No receipt found for that id"}), 404

    receipt = receipts[id]
    points = calculate_points(receipt)
    
    return jsonify({"points": points}), 200

if __name__ == '__main__':
    app.run(debug=True)
