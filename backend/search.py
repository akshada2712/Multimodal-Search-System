from typing import List, Dict
from .config import Config
from .embeddings import EmbeddingService
from .vector_store import VectorStoreManager


class SearchService:
    def __init__(self, embedding_service : EmbeddingService, vector_store_manager: VectorStoreManager):
        self.embedding_service = embedding_service
        self.text_index = vector_store_manager.text_index
        self.image_index = vector_store_manager.image_index


    def search_database(self, text_query:str = None, image_path: str = None):
        results = []
        text_weight = 0.6
        image_weight = 0.4 

        if text_query:
            text_embedding = self.embedding_service.get_text_embedding(text_query)
            text_results = self.text_index.query(
                vector=text_embedding, top_k=5, include_metadata=True
            )["matches"]

            for res in text_results:
                res["score"] *= text_weight

            results.extend(text_results)

        if image_path:
            # Generate image caption
            caption = self.embedding_service.generate_image_caption(image_path)
            print(f"Generated Caption: {caption}")

            # Image embedding
            image_embedding = self.embedding_service.get_image_embedding(image_path)
            image_results = self.image_index.query(
                vector=image_embedding, top_k=5, include_metadata=True
            )["matches"]

            for res in image_results:
                res["score"] *= image_weight

            results.extend(image_results)

            # Caption-based text search
            if caption:
                text_caption_embedding = self.embedding_service.get_text_embedding(caption)
                text_caption_results = self.text_index.query(
                    vector=text_caption_embedding, top_k=5, include_metadata=True
                )["matches"]

                for res in text_caption_results:
                    res["score"] *= text_weight

                results.extend(text_caption_results)

        unique_results = []
        seen_products = set()
        for result in sorted(results, key=lambda x: x["score"], reverse=True):
            product = result["metadata"]["product"]
            if product not in seen_products:
                # Construct full image path
                image_path = result["metadata"]["image"]
                if image_path:
                    full_image_path = f"{Config.IMAGES_DIR}/{image_path}"
                else:
                    full_image_path = None

                unique_results.append({
                    "product": product,
                    "description": result["metadata"]["description"],
                    "category": result["metadata"]["sub_product_categories"],
                    "application": result["metadata"]["application_category"],
                    "image": full_image_path,
                    "score": result["score"]
                })
                seen_products.add(product)

        return unique_results[:5]

