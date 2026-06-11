import pandas as pd
from neo4j import GraphDatabase

class KBGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def build_graph(self, filename="data_user500.csv"):
        df = pd.read_csv(filename)
        
        with self.driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            print("Cleared existing data in Neo4j.")
            
            # Create constraints (optional but recommended)
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE")
            
            # Create User nodes
            users = df['user_id'].unique()
            session.run("UNWIND $users AS user_id CREATE (:User {id: user_id})", users=users.tolist())
            print(f"Created {len(users)} User nodes.")
            
            # Create Product nodes
            products = df['product_id'].unique()
            session.run("UNWIND $products AS product_id CREATE (:Product {id: product_id})", products=products.tolist())
            print(f"Created {len(products)} Product nodes.")
            
            # Create relationships
            # Doing this in batches to avoid overwhelming Neo4j
            batch_size = 500
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                relationships = []
                for _, row in batch.iterrows():
                    relationships.append({
                        "user_id": int(row['user_id']),
                        "product_id": int(row['product_id']),
                        "action": row['action'],
                        "timestamp": row['timestamp']
                    })
                
                session.run("""
                    UNWIND $rels AS rel
                    MATCH (u:User {id: rel.user_id})
                    MATCH (p:Product {id: rel.product_id})
                    CREATE (u)-[:ACTED {action: rel.action, timestamp: rel.timestamp}]->(p)
                """, rels=relationships)
                print(f"Created batch of relationships: {i} to {min(i+batch_size, len(df))}")

if __name__ == "__main__":
    import os
    # Get the directory where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data_user500.csv")
    
    # Credentials from docker-compose
    builder = KBGraphBuilder("bolt://neo4j:7687", "neo4j", "password123")
    try:
        builder.build_graph(data_path)
        print("Knowledge Graph built successfully!")
    finally:
        builder.close()
