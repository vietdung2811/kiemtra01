import requests
import time

LAPTOP_API_URL = "http://laptop_service:8003/api/laptops/"
MOBILE_API_URL = "http://mobile_service:8004/api/mobiles/"

def add_product(url, data):
    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print(f"Successfully added {data['name']} to {url}")
        else:
            print(f"Failed to add {data['name']}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error connecting to {url}: {e}")

laptops = [
    {
        "name": "MacBook Air M2",
        "brand": "Apple",
        "price": 1199.99,
        "description": "M2 chip, 8GB RAM, 256GB SSD",
        "stock": 50
    },
    {
        "name": "MacBook Pro 14",
        "brand": "Apple",
        "price": 1999.99,
        "description": "M3 Pro, 18GB RAM, 512GB SSD",
        "stock": 30
    },
    {
        "name": "Redmi Book Pro 15",
        "brand": "Xiaomi",
        "price": 899.00,
        "description": "Intel i5, 16GB RAM, 512GB SSD",
        "stock": 20
    }
]

mobiles = [
    {
        "name": "Iphone 15 Pro",
        "brand": "Apple",
        "price": 1099.00,
        "description": "A17 Pro chip, 128GB",
        "stock": 40
    },
    {
        "name": "Iphone 14",
        "brand": "Apple",
        "price": 799.00,
        "description": "A15 chip, 128GB",
        "stock": 60
    },
    {
        "name": "Xiaomi 14",
        "brand": "Xiaomi",
        "price": 799.00,
        "description": "Snapdragon 8 Gen 3, 12GB RAM",
        "stock": 45
    },
    {
        "name": "Redmi Note 13 Pro",
        "brand": "Xiaomi",
        "price": 399.00,
        "description": "Dimensity 7200, 8GB RAM",
        "stock": 100
    }
]

if __name__ == "__main__":
    print("Adding more laptops...")
    for laptop in laptops:
        add_product(LAPTOP_API_URL, laptop)
    
    print("\nAdding more mobiles...")
    for mobile in mobiles:
        add_product(MOBILE_API_URL, mobile)

    print("\nDone!")
