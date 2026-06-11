import csv
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_data(filename="data_user500.csv", num_users=500, behaviors_per_user=8):
    actions = ["view", "click", "add_to_cart"]
    data = []
    
    start_time = datetime.now() - timedelta(days=30)
    
    for user_id in range(1, num_users + 1):
        for i in range(behaviors_per_user):
            product_id = random.randint(1, 100)
            action = random.choice(actions)
            # Make it a bit realistic: view is more common than click, click more common than add_to_cart
            action = random.choices(actions, weights=[0.6, 0.3, 0.1])[0]
            
            timestamp = start_time + timedelta(
                days=random.randint(0, 29),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            data.append([user_id, product_id, action, timestamp.strftime("%Y-%m-%d %H:%M:%S")])
    
    # Sort by user_id and timestamp
    data.sort(key=lambda x: (x[0], x[3]))
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["user_id", "product_id", "action", "timestamp"])
        writer.writerows(data)
    
    print(f"Generated {len(data)} rows in {filename}")

if __name__ == "__main__":
    generate_data()
