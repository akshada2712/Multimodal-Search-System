import os
import json
import pandas as pd
from pinecone import Pinecone, ServerlessSpec

from .config import Config
from .embeddings import EmbeddingService

class VectorStoreManager:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self._init_indices()

    def _init_indices(self):
        if Config.TEXT_INDEX_NAME not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=Config.TEXT_INDEX_NAME, 
                dimension=1536,
                metric='cosine',
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        if Config.IMAGE_INDEX_NAME not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=Config.IMAGE_INDEX_NAME, 
                dimension=512,
                metric='cosine',
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        self.text_index = self.pc.Index(Config.TEXT_INDEX_NAME)
        self.image_index = self.pc.Index(Config.IMAGE_INDEX_NAME)

    def index_data(self, csv_path: str):
        
        df = pd.read_csv(csv_path)
        df.rename(columns={
            "application": "application_category",
            "sub_application": "sub_category",
            "category": "sub_product_categories",
            "subcategory": "product"
        }, inplace=True)

        # Preprocessing
        df["text_to_embed"] = df.apply(
            lambda row: f"Product: {row['product']}. Subcategory: {row['sub_product_categories']}. "
                        f"Category: {row['sub_category']}. Description: {row['description']}. "
                        f"Applications: {row['applications']}.", axis=1
        )

        df["image"] = df["image"].apply(
            lambda x: os.path.splitext(x)[0] + ".png" if pd.notna(x) else None
        )

        text_vectors, image_vectors = [], []

        for idx, row in df.iterrows():
            # Text embedding
            text_embedding = self.embedding_service.get_text_embedding(row['text_to_embed'])

            # Prepare metadata
            metadata = {
                'application_category': row['application_category'],
                'sub_category': row['sub_category'],
                'sub_product_categories': row['sub_product_categories'],
                'product': row['product'],
                'description': row['description'],
                'applications': json.dumps(row['applications']),
                'image': row['image']
            }

            # Text vector
            text_vectors.append({
                'id': f"text_{idx}",
                'values': text_embedding,
                'metadata': {**metadata, 'type': 'text'}
            })

            # Image embedding (if image exists)
            if row['image']:
                image_path = os.path.join(Config.IMAGES_DIR, row['image'])
                if os.path.exists(image_path):
                    image_embedding = self.embedding_service.get_image_embedding(image_path)
                    image_vectors.append({
                        'id': f"image_{idx}",
                        'values': image_embedding,
                        'metadata': {**metadata, 'type': 'image'}
                    })

            # Batch upsert
            if len(text_vectors) >= 100:
                self.text_index.upsert(vectors=text_vectors)
                text_vectors = []

            if len(image_vectors) >= 100:
                self.image_index.upsert(vectors=image_vectors)
                image_vectors = []

        # Upsert remaining vectors
        if text_vectors:
            self.text_index.upsert(vectors=text_vectors)
        if image_vectors:
            self.image_index.upsert(vectors=image_vectors)