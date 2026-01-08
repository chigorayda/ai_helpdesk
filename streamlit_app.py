"""
Streamlit UI for IT Support Ticket System
"""
import streamlit as st
import asyncio
from datetime import datetime
import sys
import os
import platform
import psutil
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import HelpDeskSystem
from src.models.schemas import LLMProvider

# Helper functions for telemetry
def collect_device_telemetry():
    """Auto-detect system telemetry."""
    try:
        os_name = platform.system().lower()
        if os_name == "darwin":
            os_simple = "macos13"
        elif os_name == "windows":
            os_simple = "win11"
        else:
            os_simple = "ubuntu22"
        
        return {
            "device_id": f"streamlit-{platform.node()}",
            "os": os_simple,
            "online": True,
            "vpn_connected": False,
            "disk_critical": psutil.disk_usage('/').percent > 90,
            "cpu_pct": int(psutil.cpu_percent(interval=0.1)),
            "mem_pct": int(psutil.virtual_memory().percent),
            "uptime_hours": int((datetime.now().timestamp() - psutil.boot_time()) / 3600)
        }
    except Exception as e:
        return None

def normalize_os_value(os_value):
    """Normalize OS value to standard format (windows, macos, linux)"""
    if not os_value:
        return 'windows'
    os_lower = str(os_value).lower()
    if 'win' in os_lower:
        return 'windows'
    elif 'mac' in os_lower or 'darwin' in os_lower:
        return 'macos'
    elif 'linux' in os_lower or 'ubuntu' in os_lower:
        return 'linux'
    return 'windows'

# Sample IT questions with telemetry data
SAMPLE_QUESTIONS = [
    {
        "question": "I've been locked out of my account. I tried logging in several times but keep getting 'invalid password' errors.",
        "type": "Password Reset",
        "telemetry": {
            "device_id": "LAPTOP-USER001",
            "os": "win11",
            "online": True,
            "vpn_connected": False,
            "disk_critical": False,
            "cpu_pct": 25,
            "mem_pct": 45
        }
    },
    {
        "question": "The printer on the 3rd floor isn't working. My print job just disappeared from the queue.",
        "type": "Printer Issues",
        "telemetry": None
    },
    {
        "question": "My laptop has been running extremely slow. It takes 10 minutes to boot up and applications freeze.",
        "type": "Performance Issues",
        "telemetry": {
            "device_id": "LAPTOP-USER003",
            "os": "win11",
            "online": True,
            "vpn_connected": True,
            "disk_critical": True,
            "cpu_pct": 89,
            "mem_pct": 95,
            "uptime_hours": 336,
            "recent_errors": ["DISK_FULL_WARNING", "MEMORY_PRESSURE", "PAGE_FAULT_ERRORS"]
        }
    },
    {
        "question": "I can't connect to the office WiFi. It says 'Can't connect to this network.'",
        "type": "Network Issues",
        "telemetry": {
            "device_id": "LAPTOP-USER004",
            "os": "macos13",
            "online": False,
            "vpn_connected": False,
            "disk_critical": False,
            "cpu_pct": 30,
            "mem_pct": 60,
            "ip_assigned": False,
            "dns_resolved": False
        }
    },
    {
        "question": "I need Adobe Acrobat Pro installed. The installation keeps failing with error 1603.",
        "type": "Software Installation",
        "telemetry": {
            "device_id": "DESKTOP-USER005",
            "os": "win11",
            "online": True,
            "vpn_connected": True,
            "disk_critical": True,
            "cpu_pct": 15,
            "mem_pct": 40,
            "failed_services": ["WindowsInstaller", "MsiServer"]
        }
    },
    {
        "question": "I'm not receiving any emails since yesterday. Sending works fine but inbox hasn't updated.",
        "type": "Email Problems",
        "telemetry": {
            "device_id": "LAPTOP-USER006",
            "os": "win11",
            "online": True,
            "vpn_connected": False,
            "disk_critical": False,
            "cpu_pct": 35,
            "mem_pct": 55
        }
    },
    {
        "question": "I saved a PowerPoint yesterday but can't find it. Can you recover it from backup?",
        "type": "Lost Files",
        "telemetry": None
    },
    {
        "question": "My account is locked due to too many failed login attempts. Can you unlock it?",
        "type": "Account Lockout",
        "telemetry": None
    },
    {
        "question": "Microsoft Teams keeps crashing when I try to join video calls.",
        "type": "Application Crashes",
        "telemetry": {
            "device_id": "LAPTOP-USER009",
            "os": "macos13",
            "online": True,
            "vpn_connected": True,
            "disk_critical": False,
            "cpu_pct": 85,
            "mem_pct": 88,
            "uptime_hours": 720,
            "recent_errors": ["TEAMS_GPU_ERROR", "MEMORY_LEAK_DETECTED"]
        }
    },
    {
        "question": "My external monitor shows 'No Signal'. All cables are plugged in securely.",
        "type": "Hardware Issues",
        "telemetry": {
            "device_id": "LAPTOP-USER010",
            "os": "ubuntu22",
            "online": True,
            "vpn_connected": False,
            "disk_critical": False,
            "cpu_pct": 20,
            "mem_pct": 50,
            "recent_errors": ["DISPLAY_DRIVER_ERROR", "USB_DISCONNECT"]
        }
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

# Initialize session state for question selection and telemetry
if 'current_question_tab1' not in st.session_state:
    st.session_state.current_question_tab1 = ''
if 'current_question_tab2' not in st.session_state:
    st.session_state.current_question_tab2 = ''
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0
if 'telemetry_tab1' not in st.session_state:
    st.session_state.telemetry_tab1 = None
if 'telemetry_tab2' not in st.session_state:
    st.session_state.telemetry_tab2 = None

# Sidebar
with st.sidebar:
    st.title("🎯 IT Support Ticket System")
    st.markdown("---")
    
    st.subheader("📋 Quick Questions")
    st.markdown("*Click to use these sample IT questions*")
    
    for idx, sample in enumerate(SAMPLE_QUESTIONS):
        with st.expander(f"❓ {sample['type']}"):
            st.write(sample['question'])
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Use in Ask", key=f"sample_tab1_{idx}"):
                    st.session_state.current_question_tab1 = sample['question']
                    st.session_state.telemetry_tab1 = sample.get('telemetry')
                    st.session_state.active_tab = 0
                    st.rerun()
            with col2:
                if st.button(f"Use in Compare", key=f"sample_tab2_{idx}"):
                    st.session_state.current_question_tab2 = sample['question']
                    st.session_state.telemetry_tab2 = sample.get('telemetry')
                    st.session_state.active_tab = 1
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

# Create tabs - removed tab2 from the list to use only tab1
tab_titles = ["💬 Ask a Question", "📊 Compare Models"]
selected_tab = st.radio("", tab_titles, horizontal=True, label_visibility="collapsed", index=st.session_state.active_tab, key="tab_selector")

# Update active tab in session state
if selected_tab == tab_titles[0]:
    st.session_state.active_tab = 0
else:
    st.session_state.active_tab = 1

# Tab 1: Process single request
if st.session_state.active_tab == 0:
    st.header("Ask Your IT Question")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Use session state value directly
        question = st.text_area(
            "What do you need help with?",
            value=st.session_state.current_question_tab1,
            height=120,
            placeholder="e.g., I forgot my password and can't log in...",
            key="process_question"
        )
    
    with col2:
        model = st.selectbox(
            "Select Model",
            options=["claude", "claude-sonnet-45", "gpt4o-mini", "gpt-52", "gemini", "gemini-3-pro", "grok-4-fast", "deepseek-v32", "qwen3-235b", "llama-31-8b"],
            format_func=lambda x: {
                "claude": "🤖 Claude 3.5 Sonnet",
                "claude-sonnet-45": "🤖 Claude Sonnet 4.5",
                "gpt4o-mini": "⚡ GPT-4o Mini",
                "gpt-52": "⚡ GPT-5.2",
                "gemini": "🌟 Gemini 2.0 Flash",
                "gemini-3-pro": "🌟 Gemini 3 Pro",
                "grok-4-fast": "🚀 Grok 4 Fast",
                "deepseek-v32": "🔍 DeepSeek V3.2",
                "qwen3-235b": "🎯 Qwen3 235B",
                "llama-31-8b": "🦙 Llama 3.1 8B"
            }[x]
        )
        
        user_id = st.text_input("User ID (optional)", placeholder="user_001", key="process_user")
        
        # Speed mode toggle
        lite_mode = st.checkbox("⚡ Fast Mode", value=False, help="Skip classification & escalation for 50-70% faster responses")
        if lite_mode:
            skip_knowledge = st.checkbox("🚀 Ultra Fast", value=False, help="Also skip knowledge search for maximum speed (less accurate)")
        else:
            skip_knowledge = False
    
    # Telemetry section
    with st.expander("🔧 Device Telemetry (Optional)", expanded=False):
        st.markdown("*Raw telemetry data to help diagnose issues*")
        
        telemetry_text = st.text_area(
            "Telemetry JSON",
            value=json.dumps(st.session_state.telemetry_tab1, indent=2) if st.session_state.telemetry_tab1 else "",
            height=200,
            placeholder='{\n  "device_id": "LAPTOP-001",\n  "os": "win11",\n  "cpu_pct": 85,\n  "mem_pct": 90\n}',
            key="telemetry_text_tab1"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Auto-detect", key="auto_detect_tab1"):
                detected = collect_device_telemetry()
                if detected:
                    st.session_state.telemetry_tab1 = detected
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Clear", key="clear_tab1"):
                st.session_state.telemetry_tab1 = None
                st.rerun()
        
        # Parse telemetry JSON
        if telemetry_text.strip():
            try:
                st.session_state.telemetry_tab1 = json.loads(telemetry_text)
                st.success("✅ Telemetry data loaded")
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {e}")
                st.session_state.telemetry_tab1 = None
        else:
            st.session_state.telemetry_tab1 = None
    
    if st.button("🚀 Submit Question", type="primary", use_container_width=True):
        if not question:
            st.error("Please enter a question!")
        else:
            with st.spinner(f"Processing with {model}..."):
                try:
                    # Map model to provider
                    provider_map = {
                        "claude": LLMProvider.CLAUDE,
                        "claude-sonnet-45": LLMProvider.CLAUDE_SONNET_45,
                        "gpt4o-mini": LLMProvider.GPT4O_MINI,
                        "gpt-52": LLMProvider.GPT_52,
                        "gemini": LLMProvider.GEMINI,
                        "gemini-3-pro": LLMProvider.GEMINI_3_PRO,
                        "grok-4-fast": LLMProvider.GROK_4_FAST,
                        "deepseek-v32": LLMProvider.DEEPSEEK_V32,
                        "qwen3-235b": LLMProvider.QWEN3_235B,
                        "llama-31-8b": LLMProvider.LLAMA_31_8B
                    }
                    provider = provider_map[model]
                    
                    # Process request with appropriate workflow
                    if lite_mode:
                        st.info("⚡ Using Fast Mode - Classification and escalation skipped for speed")
                        response = system.process_request_lite(
                            request_text=question,
                            user_id=user_id if user_id else None,
                            provider=provider,
                            skip_knowledge=skip_knowledge,
                            telemetry=st.session_state.telemetry_tab1
                        )
                    else:
                        response = system.process_request_sync(
                            request_text=question,
                            user_id=user_id if user_id else None,
                            provider=provider,
                            telemetry=st.session_state.telemetry_tab1
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
if st.session_state.active_tab == 1:
    st.header("Compare AI Models")
    st.write("Select and compare multiple AI models on the same question")
    
    # Model selection with multi-select
    all_models = [
        ("claude", "🤖 Claude 3.5 Sonnet"),
        ("claude-sonnet-45", "🤖 Claude Sonnet 4.5"),
        ("gpt4o-mini", "⚡ GPT-4o Mini"),
        ("gpt-52", "⚡ GPT-5.2"),
        ("gemini", "🌟 Gemini 2.0 Flash"),
        ("gemini-3-pro", "🌟 Gemini 3 Pro"),
        ("grok-4-fast", "🚀 Grok 4 Fast"),
        ("deepseek-v32", "🔍 DeepSeek V3.2"),
        ("qwen3-235b", "🎯 Qwen3 235B"),
        ("llama-31-8b", "🦙 Llama 3.1 8B")
    ]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_models = st.multiselect(
            "Select models to compare (default: 3)",
            options=[m[0] for m in all_models],
            default=["claude", "gpt4o-mini", "gemini"],
            format_func=lambda x: dict(all_models)[x]
        )
    
    with col2:
        st.write("")
        st.write("")
        comparison_lite_mode = st.checkbox("⚡ Fast Mode", value=False, key="compare_lite", help="Use lite workflow for 50-70% faster comparison")
        if comparison_lite_mode:
            comparison_skip_knowledge = st.checkbox("🚀 Ultra Fast", value=False, key="compare_ultra", help="Skip knowledge retrieval")
        else:
            comparison_skip_knowledge = False
    
    # Use session state to maintain question value
    compare_question = st.text_area(
        "Enter your question for comparison",
        value=st.session_state.current_question_tab2,
        height=100,
        placeholder="e.g., I think I received a phishing email...",
        key="compare_question"
    )
    # Update session state with current value
    st.session_state.current_question_tab2 = compare_question
    
    compare_user_id = st.text_input("User ID (optional)", placeholder="user_001", key="compare_user")
    
    # Telemetry section for Compare tab
    with st.expander("🔧 Device Telemetry (Optional)", expanded=False):
        st.markdown("*Raw telemetry data to help diagnose issues*")
        
        telemetry_text_compare = st.text_area(
            "Telemetry JSON",
            value=json.dumps(st.session_state.telemetry_tab2, indent=2) if st.session_state.telemetry_tab2 else "",
            height=200,
            placeholder='{\n  "device_id": "LAPTOP-001",\n  "os": "win11",\n  "cpu_pct": 85,\n  "mem_pct": 90\n}',
            key="telemetry_text_tab2"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Auto-detect", key="auto_detect_tab2"):
                detected = collect_device_telemetry()
                if detected:
                    st.session_state.telemetry_tab2 = detected
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Clear", key="clear_tab2"):
                st.session_state.telemetry_tab2 = None
                st.rerun()
        
        # Parse telemetry JSON
        if telemetry_text_compare.strip():
            try:
                st.session_state.telemetry_tab2 = json.loads(telemetry_text_compare)
                st.success("✅ Telemetry data loaded")
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {e}")
                st.session_state.telemetry_tab2 = None
        else:
            st.session_state.telemetry_tab2 = None
    
    if st.button("🔬 Compare Models", type="primary", use_container_width=True):
        if not compare_question:
            st.error("Please enter a question!")
        elif not selected_models:
            st.error("Please select at least one model!")
        else:
            with st.spinner(f"Running comparison across {len(selected_models)} models... This may take a minute."):
                try:
                    # Map model strings to providers
                    provider_map = {
                        "claude": LLMProvider.CLAUDE,
                        "claude-sonnet-45": LLMProvider.CLAUDE_SONNET_45,
                        "gpt4o-mini": LLMProvider.GPT4O_MINI,
                        "gpt-52": LLMProvider.GPT_52,
                        "gemini": LLMProvider.GEMINI,
                        "gemini-3-pro": LLMProvider.GEMINI_3_PRO,
                        "grok-4-fast": LLMProvider.GROK_4_FAST,
                        "deepseek-v32": LLMProvider.DEEPSEEK_V32,
                        "qwen3-235b": LLMProvider.QWEN3_235B,
                        "llama-31-8b": LLMProvider.LLAMA_31_8B
                    }
                    
                    providers = [provider_map[m] for m in selected_models]
                    
                    # Show mode info
                    if comparison_lite_mode:
                        st.info("⚡ Using Fast Mode for comparison - Classification and escalation skipped")
                    
                    # Run comparison
                    comparison_result = asyncio.run(
                        system.compare_providers(
                            request_text=compare_question,
                            user_id=compare_user_id if compare_user_id else None,
                            providers=providers,
                            lite_mode=comparison_lite_mode,
                            skip_knowledge=comparison_skip_knowledge,
                            telemetry=st.session_state.telemetry_tab2
                        )
                    )
                    
                    st.success("✅ Comparison Complete!")
                    
                    # Winner announcement
                    winner = comparison_result.winner
                    winner_display = dict(all_models)[winner.value]
                    
                    st.markdown(f"""
                    <div style="background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; text-align: center; margin: 1rem 0;">
                        <h3>🏆 Best Performer: {winner_display}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Iterate through each provider in the comparison results
                    for provider in comparison_result.providers:
                        model_name = dict(all_models)[provider.value]
                        response_data = comparison_result.responses[provider.value]
                        metrics = comparison_result.metrics[provider.value]
                        is_winner = provider == winner
                        
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
                            "Model": [],
                            "Cost ($)": [],
                            "Time (s)": [],
                            "Confidence": [],
                            "Hallucination Risk": []
                        }
                        
                        for provider in comparison_result.providers:
                            model_name = dict(all_models)[provider.value]
                            response_data = comparison_result.responses[provider.value]
                            metrics = comparison_result.metrics[provider.value]
                            
                            comparison_data["Model"].append(model_name)
                            comparison_data["Cost ($)"].append(f"{metrics.estimated_cost:.6f}")
                            comparison_data["Time (s)"].append(f"{metrics.processing_time:.2f}")
                            comparison_data["Confidence"].append(f"{response_data.confidence:.1%}")
                            comparison_data["Hallucination Risk"].append(f"{metrics.hallucination_score:.2f}")
                        
                        df = pd.DataFrame(comparison_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🎯 IT Support Ticket System POC</p>
</div>
""", unsafe_allow_html=True)