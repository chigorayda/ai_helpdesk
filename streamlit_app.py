"""
Streamlit UI for IT Support Ticket System
"""
import streamlit as st
import asyncio
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import HelpDeskSystem
from src.models.schemas import LLMProvider

# Sample IT questions for sidebar
SAMPLE_QUESTIONS = [
    {
        "question": "I've been locked out of my account. I tried logging in several times but keep getting 'invalid password' errors.",
        "type": "Password Reset"
    },
    {
        "question": "The printer on the 3rd floor isn't working. My print job just disappeared from the queue.",
        "type": "Printer Issues"
    },
    {
        "question": "My laptop has been running extremely slow. It takes 10 minutes to boot up and applications freeze.",
        "type": "Performance Issues"
    },
    {
        "question": "I can't connect to the office WiFi. It says 'Can't connect to this network.'",
        "type": "Network Issues"
    },
    {
        "question": "I need Adobe Acrobat Pro installed. The installation keeps failing with error 1603.",
        "type": "Software Installation"
    },
    {
        "question": "I'm not receiving any emails since yesterday. Sending works fine but inbox hasn't updated.",
        "type": "Email Problems"
    },
    {
        "question": "I saved a PowerPoint yesterday but can't find it. Can you recover it from backup?",
        "type": "Lost Files"
    },
    {
        "question": "My account is locked due to too many failed login attempts. Can you unlock it?",
        "type": "Account Lockout"
    },
    {
        "question": "Microsoft Teams keeps crashing when I try to join video calls.",
        "type": "Application Crashes"
    },
    {
        "question": "My external monitor shows 'No Signal'. All cables are plugged in securely.",
        "type": "Hardware Issues"
    }
]

# Page config
st.set_page_config(
    page_title="IT Support Ticket System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .response-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        color: #000000;
        max-height: 400px;
        overflow-y: auto;
    }
    .response-box h3 {
        color: #1f77b4;
        margin-top: 0;
    }
    .response-box p {
        color: #262730;
        line-height: 1.6;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    .comparison-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    .winner-badge {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize system (cached)
@st.cache_resource
def initialize_system():
    """Initialize the help desk system once and cache it"""
    system = HelpDeskSystem()
    if system.initialize_sync():
        return system
    else:
        return None

# Get system instance
system = initialize_system()

if system is None:
    st.error("❌ Failed to initialize the Help Desk System. Please check your configuration.")
    st.stop()

# Initialize session state for question selection
if 'selected_question' not in st.session_state:
    st.session_state.selected_question = ''
if 'question_timestamp' not in st.session_state:
    st.session_state.question_timestamp = 0

# Sidebar
with st.sidebar:
    st.title("🎯 IT Support Ticket System")
    st.markdown("---")
    
    st.subheader("📋 Quick Questions")
    st.markdown("*Click to use these sample IT questions*")
    
    for idx, sample in enumerate(SAMPLE_QUESTIONS):
        with st.expander(f"❓ {sample['type']}"):
            st.write(sample['question'])
            if st.button(f"Use this question", key=f"sample_{idx}"):
                st.session_state.selected_question = sample['question']
                st.session_state.question_timestamp = idx + 1
                st.rerun()
    
    st.markdown("---")
    st.subheader("ℹ️ About")
    st.info("""
    **IT Support Ticket System**
    
    Powered by:
    - 🤖 Claude 3.5 Sonnet
    - ⚡ GPT-4o Mini
    - 🌟 Gemini 2.0 Flash
    
    Features:
    - Smart classification
    - Knowledge base retrieval
    - Auto-escalation
    - Multi-model comparison
    """)
    
    # System status
    with st.expander("📊 System Status"):
        status = system.get_system_status()
        st.write(f"**Initialized:** ✅" if status['initialized'] else "❌")
        st.write(f"**Documents:** {status['knowledge_base'].get('document_count', 0)}")

# Main content
st.markdown('<h1 class="main-header">🎯 IT Support Ticket System</h1>', unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["💬 Ask a Question", "📊 Compare Models"])

# Tab 1: Process single request
with tab1:
    st.header("Ask Your IT Question")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Get question from session state if selected from sidebar
        default_question = st.session_state.selected_question if st.session_state.question_timestamp > 0 else ''
        question = st.text_area(
            "What do you need help with?",
            value=default_question,
            height=120,
            placeholder="e.g., I forgot my password and can't log in...",
            key=f"process_question_{st.session_state.question_timestamp}"
        )
        # Clear the session state after it's loaded
        if st.session_state.question_timestamp > 0:
            st.session_state.selected_question = ''
            st.session_state.question_timestamp = 0
    
    with col2:
        model = st.selectbox(
            "Select Model",
            options=["claude", "gpt4o-mini", "gemini"],
            format_func=lambda x: {
                "claude": "🤖 Claude 3.5 Sonnet",
                "gpt4o-mini": "⚡ GPT-4o Mini",
                "gemini": "🌟 Gemini 2.0 Flash"
            }[x]
        )
        
        user_id = st.text_input("User ID (optional)", placeholder="user_001", key="process_user")
    
    if st.button("🚀 Submit Question", type="primary", use_container_width=True):
        if not question:
            st.error("Please enter a question!")
        else:
            with st.spinner(f"Processing with {model}..."):
                try:
                    # Map model to provider
                    provider_map = {
                        "claude": LLMProvider.CLAUDE,
                        "gpt4o-mini": LLMProvider.GPT4O_MINI,
                        "gemini": LLMProvider.GEMINI
                    }
                    provider = provider_map[model]
                    
                    # Process request
                    response = system.process_request_sync(
                        request_text=question,
                        user_id=user_id if user_id else None,
                        provider=provider
                    )
                    
                    # Display response
                    st.success("✅ Response Generated!")
                    
                    # Response card
                    st.markdown(f"""
                    <div class="response-box">
                        <h3>💡 Response</h3>
                        <p>{response.response}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Metrics in columns
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📁 Category", response.category.value.replace('_', ' ').title())
                    
                    with col2:
                        st.metric("🎯 Confidence", f"{response.confidence:.1%}")
                    
                    with col3:
                        st.metric("⏱️ Processing Time", f"{response.processing_time:.2f}s")
                    
                    with col4:
                        escalation = "Yes ⚠️" if response.escalation.should_escalate else "No ✅"
                        st.metric("🚨 Escalation", escalation)
                    
                    # Additional details in expander
                    with st.expander("📋 View Details"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Escalation Info")
                            st.write(f"**Priority:** {response.escalation.priority.value}")
                            st.write(f"**Department:** {response.escalation.suggested_department}")
                            st.write(f"**Reasoning:** {response.escalation.reasoning}")
                        
                        with col2:
                            st.subheader("Knowledge Sources")
                            if response.knowledge_sources:
                                for source in response.knowledge_sources:
                                    st.write(f"- {source}")
                            else:
                                st.write("*No knowledge sources used*")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

# Tab 2: Compare models
with tab2:
    st.header("Compare AI Models")
    st.write("See how Claude, GPT-4o Mini, and Gemini perform on the same question")
    
    # Get question from session state if selected from sidebar
    default_question_compare = st.session_state.selected_question if st.session_state.question_timestamp > 0 else ''
    compare_question = st.text_area(
        "Enter your question for comparison",
        value=default_question_compare,
        height=100,
        placeholder="e.g., I think I received a phishing email...",
        key=f"compare_question_{st.session_state.question_timestamp}"
    )
    # Clear the session state after it's loaded
    if st.session_state.question_timestamp > 0:
        st.session_state.selected_question = ''
        st.session_state.question_timestamp = 0
    
    compare_user_id = st.text_input("User ID (optional)", placeholder="user_001", key="compare_user")
    
    if st.button("🔬 Compare Models", type="primary", use_container_width=True):
        if not compare_question:
            st.error("Please enter a question!")
        else:
            with st.spinner("Running comparison across all models... This may take a minute."):
                try:
                    # Run comparison
                    comparison_result = asyncio.run(
                        system.compare_providers(
                            request_text=compare_question,
                            user_id=compare_user_id if compare_user_id else None
                        )
                    )
                    
                    st.success("✅ Comparison Complete!")
                    
                    # Winner announcement
                    winner = comparison_result.winner
                    winner_name = {
                        LLMProvider.CLAUDE: "🤖 Claude 3.5 Sonnet",
                        LLMProvider.GPT4O_MINI: "⚡ GPT-4o Mini",
                        LLMProvider.GEMINI: "🌟 Gemini 2.0 Flash"
                    }[winner]
                    
                    st.markdown(f"""
                    <div style="background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; text-align: center; margin: 1rem 0;">
                        <h3>🏆 Best Performer: {winner_name}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create comparison cards for each model
                    models = [
                        (LLMProvider.CLAUDE, "🤖 Claude 3.5 Sonnet", comparison_result.claude_response, comparison_result.claude_metrics),
                        (LLMProvider.GPT4O_MINI, "⚡ GPT-4o Mini", comparison_result.gpt4o_mini_response, comparison_result.gpt4o_mini_metrics),
                        (LLMProvider.GEMINI, "🌟 Gemini 2.0 Flash", comparison_result.gemini_response, comparison_result.gemini_metrics)
                    ]
                    
                    for model_id, model_name, response_data, metrics in models:
                        is_winner = model_id == winner
                        
                        with st.container():
                            # Model header with winner badge
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.subheader(model_name)
                            with col2:
                                if is_winner:
                                    st.markdown('<span class="winner-badge">🏆 WINNER</span>', unsafe_allow_html=True)
                            
                            # Metrics
                            col1, col2, col3, col4, col5 = st.columns(5)
                            
                            with col1:
                                st.metric("💰 Cost", f"${metrics.estimated_cost:.6f}")
                            
                            with col2:
                                st.metric("⏱️ Time", f"{metrics.processing_time:.2f}s")
                            
                            with col3:
                                st.metric("🎯 Confidence", f"{response_data.confidence:.1%}")
                            
                            with col4:
                                st.metric("✨ Quality", f"{metrics.response_quality:.1%}")
                            
                            with col5:
                                hallucination_color = "🟢" if metrics.hallucination_score < 0.3 else "🟡" if metrics.hallucination_score < 0.6 else "🔴"
                                st.metric("🎲 Risk", f"{hallucination_color} {metrics.hallucination_score:.2f}")
                            
                            # Response in expander
                            with st.expander(f"📄 View {model_name} Response"):
                                st.markdown(f"**Response:**")
                                st.info(response_data.response)
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Category:** {response_data.category.value.replace('_', ' ').title()}")
                                    
                                    if response_data.escalation.should_escalate:
                                        st.warning(f"⚠️ Escalation Required - Priority: {response_data.escalation.priority.value}")
                                    else:
                                        st.success("✅ No escalation needed")
                                
                                with col2:
                                    st.markdown(f"**Knowledge Sources:** {len(response_data.knowledge_sources)}")
                                    if response_data.knowledge_sources:
                                        for source in response_data.knowledge_sources[:3]:  # Show first 3
                                            st.caption(f"- {source.split('/')[-1]}")
                            
                            st.markdown("---")
                    
                    # Summary comparison table
                    with st.expander("📊 Summary Comparison Table"):
                        import pandas as pd
                        
                        comparison_data = {
                            "Model": ["Claude 3.5 Sonnet", "GPT-4o Mini", "Gemini 2.0 Flash"],
                            "Cost ($)": [
                                f"{comparison_result.claude_metrics.estimated_cost:.6f}",
                                f"{comparison_result.gpt4o_mini_metrics.estimated_cost:.6f}",
                                f"{comparison_result.gemini_metrics.estimated_cost:.6f}"
                            ],
                            "Time (s)": [
                                f"{comparison_result.claude_metrics.processing_time:.2f}",
                                f"{comparison_result.gpt4o_mini_metrics.processing_time:.2f}",
                                f"{comparison_result.gemini_metrics.processing_time:.2f}"
                            ],
                            "Confidence": [
                                f"{comparison_result.claude_response.confidence:.1%}",
                                f"{comparison_result.gpt4o_mini_response.confidence:.1%}",
                                f"{comparison_result.gemini_response.confidence:.1%}"
                            ],
                            "Hallucination Risk": [
                                f"{comparison_result.claude_metrics.hallucination_score:.2f}",
                                f"{comparison_result.gpt4o_mini_metrics.hallucination_score:.2f}",
                                f"{comparison_result.gemini_metrics.hallucination_score:.2f}"
                            ]
                        }
                        
                        df = pd.DataFrame(comparison_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🎯 IT Support Ticket System | Powered by OpenRouter | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
