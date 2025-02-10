import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    # Index Names
    TEXT_INDEX_NAME = "renesas-search-text"
    IMAGE_INDEX_NAME = "renesas-search-image"

    # Paths
    BASE_DIR = "Renesas_Scraper"
    DATA_DIR = os.path.join(BASE_DIR, "data")
    IMAGES_DIR = os.path.join(BASE_DIR, "converted_png")
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # DATA_DIR = os.path.join(BASE_DIR, "data")
    # IMAGES_DIR = os.path.join(DATA_DIR, "images")
    
    # Embedding Configurations
    TEXT_EMBED_MODEL = "text-embedding-3-small"
    IMAGE_EMBED_MODEL = "openai/clip-vit-base-patch32"