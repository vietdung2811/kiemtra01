from django.core.management.base import BaseCommand
from api.models import ProductMetadata
from sentence_transformers import SentenceTransformer
import numpy as np

class Command(BaseCommand):
    help = 'Populates embeddings for all existing products'

    def handle(self, *args, **options):
        self.stdout.write("Loading model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        products = ProductMetadata.objects.filter(embedding__isnull=True)
        count = products.count()
        self.stdout.write(f"Found {count} products without embeddings.")
        
        for i, product in enumerate(products):
            text = f"{product.brand} {product.name} {product.description}"
            self.stdout.write(f"[{i+1}/{count}] Encoding: {product.name}...")
            embedding = model.encode(text)
            product.embedding = embedding.tobytes()
            product.save()
            
        self.stdout.write(self.style.SUCCESS('Successfully populated embeddings.'))
