# app.py - Your main chatbot application
import streamlit as st
from groq import Groq
import time
from datetime import datetime
import config
import utils

# Page setup (make it look professional)
st.set_page_config(
    page_title="🌍 Global Free Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for better look
st.markdown("""
    <style>
    .stChatInput {
        padding-bottom: 20px;
    }
    .stButton button {
        width: 100%;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🌍 Global Free Chatbot")
st.markdown("""
    **Free • Multilingual • Answers Everything**  
    Built with Groq's free AI. Understands 20+ languages. No credit card needed.
""")

# Sidebar with information
with st.sidebar:
    st.header("📊 Status")
    st.metric("Model", config.Config.MODEL_NAME)
    st.metric("Language Support", "20+ Languages")
    st.metric("Knowledge Base", "Wikipedia + Real-time")
    
    st.divider()
    
    st.header("💡 Tips")
    st.info("""
    - Ask in ANY language
    - Get instant answers
    - 100% Free
    - No sign-up needed
    """)
    
    st.divider()
    
    st.header("🌐 Supported Languages")
    langs = {
        "English": "🇬🇧", "Hindi": "🇮🇳", "Spanish": "🇪🇸", 
        "French": "🇫🇷", "German": "🇩🇪", "Chinese": "🇨🇳",
        "Arabic": "🇸🇦", "Japanese": "🇯🇵", "Korean": "🇰🇷",
        "Portuguese": "🇵🇹", "Russian": "🇷🇺", "Italian": "🇮🇹"
    }
    for lang, flag in list(langs.items())[:6]:
        st.write(f"{flag} {lang}")
    st.caption("+ Many more languages!")

# Initialize the Groq client (free!)
@st.cache_resource
def init_groq():
    try:
        if not config.Config.GROQ_API_KEY:
            st.error("⚠️ GROQ_API_KEY not found! Please add it to .env file")
            return None
        return Groq(api_key=config.Config.GROQ_API_KEY)
    except Exception as e:
        st.error(f"Failed to connect to Groq: {e}")
        return None

client = init_groq()

# Initialize session state (keep conversation history)
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "language" in message:
            st.caption(f"Detected language: {message['language']}")

# Chat input
if prompt := st.chat_input("Ask me anything in any language..."):
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.total_questions += 1
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Detect language
    detected_lang = utils.detect_language(prompt)
    
    # Check cache first (for speed)
    cached_answer = utils.get_from_cache(prompt)
    
    if cached_answer:
        # Use cached answer (saves money and time)
        response = cached_answer
        from_cache = True
    else:
        from_cache = False
        
        # Search local knowledge base
        knowledge = utils.search_knowledge(prompt)
        context = "\n".join(knowledge) if knowledge else ""
        
        # Prepare the system prompt with language instruction
        system_prompt = f"""You are a free, global AI assistant that helps everyone.

CRITICAL RULES:
1. ALWAYS respond in {detected_lang} language
2. Be helpful, friendly, and accurate
3. Use this knowledge if helpful: {context}
4. If you don't know, say "I don't have that information" in {detected_lang}
5. Keep answers clear and concise
6. Be safe - don't help with illegal or harmful things"""
        
        # Prepare the conversation for Groq
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add last 5 messages for context
        # Add last 5 messages for context (ONLY role and content!)
    for msg in st.session_state.messages[-5:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
    })
        
        # Get response from Groq (FREE!)
        try:
            if client:
                with st.spinner("🤔 Thinking..."):
                    completion = client.chat.completions.create(
                        model=config.Config.MODEL_NAME,
                        messages=messages,
                        temperature=config.Config.TEMPERATURE,
                        max_tokens=config.Config.MAX_TOKENS,
                        top_p=0.9,
                    )
                    response = completion.choices[0].message.content
                    
                    # Save to cache for next time
                    utils.save_to_cache(prompt, response)
                    
                    # Add to knowledge base
                    utils.add_to_knowledge(prompt, {"language": detected_lang})
            else:
                response = "⚠️ Sorry, I can't connect to the AI. Please check your API key."
                
        except Exception as e:
            response = f"⚠️ Error: {str(e)}"
    
    # Format the response
    formatted_response = utils.format_response(response, detected_lang)
    
    # Add assistant response to history
   # Add assistant response to history (NO language field!)
    st.session_state.messages.append({
        "role": "assistant", 
        "content": formatted_response
    # REMOVED: "language": detected_lang
    })
    
    # Display assistant response
    with st.chat_message("assistant"):
        if from_cache:
            st.markdown(f"💨 **From Memory:** {formatted_response}")
        else:
            st.markdown(formatted_response)
            if knowledge:
                st.caption("📚 Based on: Local knowledge + AI")
            else:
                st.caption("🧠 Based on: AI knowledge")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"💬 {st.session_state.total_questions} questions asked")
with col2:
    st.caption("⚡ Powered by Groq (Free)")
with col3:
    st.caption("🌍 Works in 20+ languages")

# Add a clear chat button in sidebar
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Show system status
if st.sidebar.button("🔄 Check Status"):
    if client:
        st.sidebar.success("✅ Connected to Groq API")
        st.sidebar.info(f"📊 Cache size: {len(utils.cache)} items")
        try:
            db_count = utils.collection.count()
            st.sidebar.info(f"📚 Knowledge base: {db_count} items")
        except:
            st.sidebar.info("📚 Knowledge base: 0 items")
    else:
        st.sidebar.error("❌ Not connected to Groq")