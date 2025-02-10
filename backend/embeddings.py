import base64
from typing import List
from PIL import Image
from openai import OpenAI
from transformers import CLIPProcessor, CLIPModel


from .config import Config

class EmbeddingService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.clip_model = CLIPModel.from_pretrained(Config.IMAGE_EMBED_MODEL)
        self.clip_processor = CLIPProcessor.from_pretrained(Config.IMAGE_EMBED_MODEL)

    def get_text_embedding(self, text):
        response = self.openai_client.embeddings.create(
            model=Config.TEXT_EMBED_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    def get_image_embedding(self, image_path):
        image = Image.open(image_path)
        inputs = self.clip_processor(images=image, return_tensors="pt")
        image_features = self.clip_model.get_image_features(**inputs)
        return image_features.detach().numpy().flatten().tolist()
    
    def generate_image_caption(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": 
                        "You are an AI specialized in analyzing engineering systems from images. "
                        "Provide a concise, technical description of the system's key components and functionality."},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Describe this technical system or block diagram."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Image captioning error: {e}")
            return ""