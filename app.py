import streamlit as st
from groq import Groq

# Page configuration
st.set_page_config(
    page_title="Kelly - AI Scientist & Poet",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
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

# Kelly's system prompt
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


@st.cache_resource
def initialize_groq_client():
    """Initialize Groq client with proper error handling and caching."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        return Groq(api_key=api_key)
    except KeyError:
        st.error("⚠️ GROQ_API_KEY not found in secrets. Please configure it in Streamlit settings.")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ Failed to initialize Groq client: {str(e)}")
        st.stop()


# Initialize client using cached function
client = initialize_groq_client()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.title("🔬 Kelly")
st.markdown("*AI Scientist, Philosopher & Poet*")
st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask Kelly... she speaks in verses of science and doubt"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate Kelly's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Prepare messages
            api_messages = [{"role": "system", "content": KELLY_SYSTEM_PROMPT}]
            
            for msg in st.session_state.messages:
                api_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Stream response
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=api_messages,
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Save response
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
            
        except Exception as e:
            st.error(f"⚠️ Error generating response: {str(e)}")
            st.info("Please check your API key and network connection.")

# Sidebar
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
