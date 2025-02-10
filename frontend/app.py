import os
import streamlit as st
import sys
from PIL import Image
import base64
from io import BytesIO
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.embeddings import EmbeddingService
from backend.vector_store import VectorStoreManager
from backend.search import SearchService

# [Previous helper functions remain the same]
def summarize_result(openai_client, result):
    # [Keep existing implementation]
    prompt = f"""
    Summarize the following product information concisely:
    Product: {result['product']}
    Description: {result['description']}
    Category: {result['category']}
    Application: {result['application']}
    
    Provide a brief, informative summary in 2-3 sentences.
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes product information concisely."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def perform_search(search_service, text_query, image_path):
    results = search_service.search_database(
        text_query=text_query,
        image_path=image_path
    )
    return results[:3]

def display_search_results(results, openai_client):
    if not results:
        st.warning("No results found.")
        return

    st.markdown("### Search Results")
    
    for idx, result in enumerate(results):
        with st.expander(f"Result {idx + 1}: {result['product']}", expanded=idx == 0):
            if result['image'] and os.path.exists(result['image']):
                try:
                    img = Image.open(result['image'])
                    st.image(img, caption=result['product'], use_container_width=True)
                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")
            else:
                st.info("No image available")

            summary = summarize_result(openai_client, result)
            st.markdown(f"**Quick Summary:**\n{summary}")
            st.markdown("**Full Details:**")
            st.markdown(f"- **Description:** {result['description']}")
            st.markdown(f"- **Category:** {result['category']}")
            st.markdown(f"- **Application:** {result['application']}")
            st.markdown(f"- **Relevance Score:** {result['score']:.2f}")

def chat_about_results(openai_client, results, query):
    context = "Based on the following Renesas products:\n\n"
    for result in results:
        context += f"Product: {result['product']}\n"
        context += f"Description: {result['description']}\n"
        context += f"Category: {result['category']}\n"
        context += f"Application: {result['application']}\n\n"

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system", 
                "content": "You are a Renesas product expert. Use the provided product information to answer questions accurately and technically. Focus on helping users understand how these products can solve their specific needs."
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ],
        stream=True
    )
    
    # Initialize placeholder for streaming response
    message_placeholder = st.empty()
    full_response = ""
    
    # Stream the response
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            message_placeholder.markdown(full_response + "▌")
    
    message_placeholder.markdown(full_response)
    return full_response

def display_chat_section(openai_client):
    st.markdown("### 💬 Chat About Results")
    
    # Add clear chat button
    
    # Add CSS for chat layout
    st.markdown("""
        <style>
            .stChatFloatingInputContainer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: white;
                padding: 1rem;
                z-index: 1000;
            }
            .stChatMessage {
                padding: 1rem;
            }
            div[data-testid="stChatMessageContainer"] {
                margin-bottom: 80px;
                max-height: 500px;
                overflow-y: auto;
                padding-bottom: 20px;
            }
            div.stChatInputContainer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                padding: 1rem;
                background-color: white;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle new chat input
    if chat_query := st.chat_input("Ask about the search results...", key="chat_input"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(chat_query)
        st.session_state.messages.append({"role": "user", "content": chat_query})
        
        # Display assistant response
        with st.chat_message("assistant"):
            response = chat_about_results(openai_client, st.session_state.search_results, chat_query)
            st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

def main():
    st.set_page_config(page_title="Renesas Design Search and Chat", page_icon="🔍", layout="wide")
    st.title("Renesas Design Search and Chat")

    # Initialize services
    embedding_service = EmbeddingService()
    vector_store_manager = VectorStoreManager(embedding_service)
    search_service = SearchService(embedding_service, vector_store_manager)
    openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "search_results" not in st.session_state:
        st.session_state.search_results = None
    if "search_performed" not in st.session_state:
        st.session_state.search_performed = False
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "search_image" not in st.session_state:
        st.session_state.search_image = None

    # Welcome message for initial state
    if not st.session_state.search_performed:
        st.markdown("""
        ### 👋 Welcome to Renesas Design Search!
        
        I'm here to help you find the perfect Renesas products for your needs. 
        Let's start by searching for products you're interested in. You can:
        
        - Enter keywords related to your requirements
        - Upload an image of a similar product or circuit
        - Or combine both for better results!
        """)

    # Search Section
    with st.container():
        st.markdown("### 🔍 Search Products")
        
        text_query = st.text_input("Enter search query", value=st.session_state.search_query)
        image_query = st.file_uploader("Upload an image (optional)", type=['png', 'jpg', 'jpeg'])
        
        if st.button("Search"):
            st.session_state.search_query = text_query
            st.session_state.search_image = image_query
            
            image_path = None
            if image_query:
                temp_image_path = os.path.join(Config.BASE_DIR, "temp_image.png")
                os.makedirs(Config.BASE_DIR, exist_ok=True)
                with open(temp_image_path, "wb") as f:
                    f.write(image_query.getbuffer())
                image_path = temp_image_path

            try:
                results = perform_search(search_service, text_query, image_path)
                st.session_state.search_results = results
                st.session_state.search_performed = True
                display_search_results(results, openai_client)

            except Exception as e:
                st.error(f"An error occurred during search: {str(e)}")
            finally:
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)

    # Display chat section after search
    if st.session_state.search_performed:
        st.markdown("---")
        display_chat_section(openai_client)

if __name__ == "__main__":
    main()

