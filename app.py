import streamlit as st
import os
import time
from studymate import StudyMate
from config import MAX_FILE_SIZE, ALLOWED_EXTENSIONS

# Configure Streamlit page
st.set_page_config(
    page_title="StudyMate - AI Academic Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize StudyMate in session state
if 'studymate' not in st.session_state:
    st.session_state.studymate = StudyMate()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def main():
    """Main Streamlit application with clean home page design."""
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .upload-section {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .question-section {
            background: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            margin-bottom: 2rem;
        }
        .chat-message {
            background: #f1f3f4;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .user-message {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .assistant-message {
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
        <div class="main-header">
            <h1>📚 StudyMate - AI Academic Assistant (Granite 3.3 2B)</h1>
            <p>Upload your study materials and ask questions with enhanced AI reasoning</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get system status
    status = st.session_state.studymate.get_system_status()
    
    # Main layout - two columns
    col1, col2 = st.columns([1, 1])
    
    # Left column - Document Upload
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.subheader("📄 Upload Study Materials")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Choose PDF files to analyze",
            type=['pdf'],
            accept_multiple_files=True,
            help=f"Upload one or more PDF files (max {MAX_FILE_SIZE // (1024*1024)}MB each)",
            key="file_uploader"
        )
        
        # Process uploaded files
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} file(s) selected")
            
            if st.button("🚀 Process Documents", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing your documents..."):
                    results = st.session_state.studymate.upload_documents(uploaded_files)
                    
                    if results['success']:
                        st.success(f"✅ Successfully processed {len(results['processed_files'])} documents!")
                        st.info(f"📊 Total text chunks created: {results['total_chunks']}")
                        
                        # Show processed files
                        with st.expander("📋 View Processed Files"):
                            for file_info in results['processed_files']:
                                st.write(f"📄 **{file_info['filename']}**: {file_info['chunks']} chunks ({file_info['size']:,} bytes)")
                    else:
                        st.error("❌ Error processing documents:")
                        for error in results['errors']:
                            st.error(f"• {error}")
        
        # System status display
        st.markdown("### ⚙️ System Status")
        
        if status['initialized']:
            st.success("✅ System Ready")
            st.metric("📁 Loaded Files", len(status['uploaded_files']))
            
            # Show vector store stats
            if status['vector_store_stats']:
                stats = status['vector_store_stats']
                st.metric("📊 Document Chunks", stats.get('total_documents', 0))
        else:
            st.warning("⚠️ No documents uploaded yet")
        
        # LLM connection status
        if status['llm_connection']:
            st.success("🤖 AI Model: Ready")
        else:
            st.warning("🤖 AI Model: Demo Mode")
            st.info("💡 Upload documents and ask questions to see the demo in action!")
        
        # Sample PDF download
        if os.path.exists("c:\\Users\\avida\\code\\sample_study_material.pdf"):
            with open("c:\\Users\\avida\\code\\sample_study_material.pdf", "rb") as file:
                st.download_button(
                    label="📥 Download Sample PDF",
                    data=file.read(),
                    file_name="sample_study_material.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        # Clear session button
        if st.button("🗑️ Clear Session", use_container_width=True):
            st.session_state.studymate.clear_session()
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Right column - Questions and Answers
    with col2:
        st.markdown('<div class="question-section">', unsafe_allow_html=True)
        st.subheader("💬 Ask Questions")
        
        # Question input
        question = st.text_area(
            "What would you like to know about your study materials?",
            placeholder="Examples:\n• What are the main concepts in Chapter 1?\n• Explain machine learning algorithms\n• Summarize the key points about AI ethics",
            height=100,
            key="question_input"
        )
        
        # Ask button
        col_ask, col_clear = st.columns([3, 1])
        with col_ask:
            ask_clicked = st.button("🤔 Ask Question", type="primary", use_container_width=True)
        with col_clear:
            clear_clicked = st.button("🧹 Clear", use_container_width=True)
        
        if clear_clicked:
            st.session_state.question_input = ""
            st.rerun()
        
        # Process question
        if ask_clicked and question and len(question.strip()) > 2:
            with st.spinner("🤔 Thinking..."):
                # Get answer
                start_time = time.time()
                response = st.session_state.studymate.ask_question(question)
                response_time = time.time() - start_time
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'question': question,
                    'response': response,
                    'timestamp': time.time(),
                    'response_time': response_time
                })
                
                # Clear input
                st.session_state.question_input = ""
                st.rerun()
        
        elif ask_clicked and (not question or len(question.strip()) <= 2):
            st.warning("⚠️ Please enter a question with at least 3 characters.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat History Section (Full Width)
    if st.session_state.chat_history:
        st.markdown("### 📝 Conversation History")
        
        # Display chat history
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5 conversations
            with st.expander(f"💬 {chat['question'][:80]}{'...' if len(chat['question']) > 80 else ''}", expanded=i==0):
                
                # Question
                st.markdown('<div class="chat-message user-message">', unsafe_allow_html=True)
                st.markdown(f"**❓ Your Question:**\n{chat['question']}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Answer
                st.markdown('<div class="chat-message assistant-message">', unsafe_allow_html=True)
                if chat['response']['success']:
                    st.markdown(f"**🤖 StudyMate's Answer:**\n{chat['response']['answer']}")
                    
                    # Confidence score and response time
                    col_conf, col_time = st.columns([1, 1])
                    with col_conf:
                        confidence = chat['response']['confidence']
                        if confidence > 0:
                            st.progress(confidence, text=f"Confidence: {confidence:.1%}")
                    
                    with col_time:
                        st.caption(f"⏱️ Response time: {chat['response_time']:.2f}s")
                    
                    # Show sources if available
                    if chat['response']['sources']:
                        st.markdown("**� Sources:**")
                        for j, source in enumerate(chat['response']['sources'][:3]):  # Show top 3 sources
                            st.markdown(f"• **{source['filename']}** (Relevance: {source['relevance_score']:.1%})")
                            
                else:
                    st.error(f"❌ Error: {chat['response']['answer']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Welcome message when no conversations yet
        st.markdown("### 🎯 Get Started")
        
        col_welcome1, col_welcome2 = st.columns([1, 1])
        with col_welcome1:
            st.markdown("""
                **📄 Step 1: Upload Documents**
                - Click "Choose PDF files" to upload your study materials
                - Support for multiple PDFs at once
                - Automatic text extraction and processing
            """)
        
        with col_welcome2:
            st.markdown("""
                **💬 Step 2: Ask Questions**
                - Type your questions in natural language
                - Get contextual answers from your documents
                - View sources and confidence scores
            """)
        
        # Quick tips
        st.info("""
            💡 **Quick Tips:**
            - Ask specific questions for better answers
            - Try questions like "What is..." or "Explain..."
            - Use the sample PDF to test the system
            - View conversation history to track your learning
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>🤖 Powered by IBM Granite 3.3 2B • 🧠 Enhanced Reasoning • 🔍 FAISS Vector Search</p>
            <p><em>StudyMate - Your AI Academic Assistant for Intelligent Document Interaction</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_configuration_help():
    """Display configuration help."""
    st.header("⚙️ Configuration")
    
    st.markdown("""
    ### Granite 3.3 2B Model Setup
    
    StudyMate now uses IBM's Granite 3.3 2B model via Hugging Face:
    
    1. **Automatic Model Download:**
       - The model will download automatically on first use (~4.5GB)
       - Requires internet connection for initial download
       - Subsequent runs use cached model
    
    2. **Optional: Hugging Face Token (for faster downloads):**
       - Create account at [Hugging Face](https://huggingface.co/)
       - Get your access token from profile settings
       - Add to `.env` file:
         ```
         HUGGINGFACE_TOKEN=your_token_here
         ```
    
    3. **Hardware Requirements:**
       - **GPU**: NVIDIA CUDA-compatible (8GB+ VRAM recommended)
       - **CPU**: 16GB+ RAM for CPU inference
       - **Storage**: At least 10GB free space
    
    4. **No additional credentials required!**
       - The model runs locally after download
       - No external API keys needed
    """)

if __name__ == "__main__":
    main()
    
        