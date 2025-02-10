# Multimodal Circuit Design Search System using LLM and RAG

## Overview
This project is designed to crawl and index all available winning combination designs from Renesas Electronics. It integrates a search and query system built using Streamlit, allowing users to identify required designs and interact with the design descriptions via chat. The system also indexes design diagrams and displays them wherever relevant to the answers.

### Problem Statement
Many engineers and developers face challenges when working with circuit designs or choosing the right Renesas products for their specific use cases. This system helps users in two primary ways:
1. **Product Understanding:** If a user has a specific product in mind and wants to explore its potential applications, they can use this system to retrieve relevant Renesas solutions.
2. **Circuit Troubleshooting:** If a user is working on a circuit diagram and is unsure about a component or its potential use, the system helps identify relevant Renesas products and guides them through its applications.

The system enables users to search using both text and images, making it an intelligent assistant for engineers and hardware developers.

## Project Structure
```
search_system/
│── backend/
│   │── __init__.py
│   │── config.py
│   │── crawl_pipeline.py
│   │── embeddings.py
│   │── search.py
│   │── vector_store.py
│── frontend/
│   │── Renesas_Scraper/
│   │── __init__.py
│   │── app.py
│   │── utils.py
│── Renesas_Scraper/
```

## Features
### 1. Text Search
- Converts the user’s text query into text embeddings.
- Searches the text vector database for relevant design descriptions.

### 2. Image Search (Real-World Image Handling)
- Uses OpenAI’s GPT-4 Vision model to generate a text-based caption of an uploaded image.
- Converts the generated caption into an embedding.
- Searches both text and image databases to find relevant block diagrams.

### 3. Hybrid Search (Both Text + Image)
- Combines results from both image and text embeddings.
- Ranks results based on similarity scores for better accuracy.

## Technology Stack

### **Embeddings**
- We use **OpenAI's GPT-based models** to generate high-quality embeddings for both text and images.
- These embeddings help in understanding the semantic meaning of queries and matching them effectively with stored designs.

### **Vector Database (Pinecone)**
- **Pinecone** is used to store and retrieve embeddings efficiently.
- It enables fast, scalable, and real-time similarity searches across large datasets of design descriptions and diagrams.

### **GPT-4 Vision for Image Understanding**
- GPT-4 Vision processes images to generate captions and understand their context.
- The extracted text descriptions are embedded and stored for multimodal search capabilities.

### **Streamlit for UI**
- The frontend is built using **Streamlit**, providing an interactive and user-friendly interface for searching and querying Renesas designs.

## Backend Modules

### `config.py`
Handles configuration settings, such as API keys, file paths, and database connections.

### `crawl_pipeline.py`
Scrapes and indexes all available winning combination designs from Renesas Electronics.

### `embeddings.py`
Processes text data and images into embeddings using a pre-trained model for semantic search.

### `search.py`
Implements search functionalities for text, image, and hybrid search.

### `vector_store.py`
Manages the storage and retrieval of vector embeddings to optimize search efficiency.

## Frontend Modules

### `app.py`
Main application file that serves as the user interface using Streamlit, integrating backend functionalities for interactive querying and chat.

### `utils.py`
Contains helper functions used across the frontend application.

## Installation
To set up and run the project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/akshada2712/Multimodal-Search-System.git
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate 
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   streamlit run frontend/app.py
   ```

## Usage
- The backend scrapes, processes, and stores Renesas designs.
- The frontend provides an interface for text, image, and hybrid search.
- Users can query relevant designs and interact with them via chat.
- Indexed design diagrams are shown in relevant search results.
- Engineers can search for solutions based on a product name or upload a circuit diagram to identify relevant components.

## Future Enhancements
- Implement real-time updates for newly added Renesas designs.
- Improve search ranking algorithms with reinforcement learning.
- Enhance UI/UX with better visualization tools.

## Contributions
Feel free to open issues and submit pull requests for improvements.

