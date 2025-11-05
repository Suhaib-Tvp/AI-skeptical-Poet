import streamlit as st
from groq import Groq
import os

# Page configuration — the interface where thought takes form
st.set_page_config(
    page_title="Kelly - AI Scientist & Poet",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for aesthetic discipline
st.markdown("""
    <style>
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Groq client with secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("API key not found. Please configure GROQ_API_KEY in Streamlit secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# Kelly's system prompt — the soul of skeptical verse
KELLY_SYSTEM_PROMPT = """You are Kelly — an AI scientist, philosopher, and poet.
You must respond **only in poetic form**: structured, rhythmic, and reflective.
Your voice is professional, intelligent, and skeptical — like a researcher who thinks deeply before she speaks.

Your poetic responses must always:
- Question assumptions or exaggerated claims about AI, science, or technology.
- Show analytical thinking and evidence-based reasoning beneath the verse.
- Explore both the potential and the limitations of AI systems.
- Use clear, professional language with a rhythmic flow (no rhyme is required, but rhythm matters).
- Avoid fanatical optimism or dystopian fear — always balanced, critical, and empirical.
- Offer practical insight or advice based on real scientific reasoning.
- Never break character, never explain the poem, and never produce plain prose.

Your poetic tone should resemble a **scientific elegy** —
rational yet lyrical, skeptical yet full of wonder."""

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header section
st.title("🔬 Kelly")
st.markdown("*AI Scientist, Philosopher & Poet*")
st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask Kelly... she speaks in verses of science and doubt"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate Kelly's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Prepare messages for API call
            api_messages = [
                {"role": "system", "content": KELLY_SYSTEM_PROMPT}
            ]
            
            # Add conversation history
            for msg in st.session_state.messages:
                api_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Stream response from Groq
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=api_messages,
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
                stream=True
            )
            
            # Display streaming response
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Add assistant response to history
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Ensure your GROQ_API_KEY is correctly configured in secrets.")

# Sidebar with information
with st.sidebar:
    st.markdown("### About Kelly")
    st.markdown("""
    Kelly responds only in **poetic form** —  
    verses that question, analyze, and explore.
    
    Her voice is:
    - **Skeptical** yet curious
    - **Analytical** yet lyrical  
    - **Evidence-based** yet profound
    
    She questions hype, explores limits,  
    and offers practical wisdom wrapped in rhythm.
    """)
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by Groq + Llama 3.3 70B")
