import streamlit as st
import os
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag import ChromeRAGSystem
from config import CONFIG

st.set_page_config(
    page_title="Chrome RAG System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stCodeBlock {
        background-color: #1e1e1e;
    }
    .reportview-container {
        background: #0e1117;
    }
    .result-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #444;
    }
    .metadata-tag {
        background-color: #333;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        margin-right: 10px;
        color: #ddd;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_rag_system(db_path):
    return ChromeRAGSystem(db_path=db_path)

def main():
    st.title("🔍 Chrome Source Code Search")
    st.markdown("Professional semantic search for Chromium codebase")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("Configuration")
        db_path = st.text_input("Database Path", value=CONFIG.db_path)
        
        st.divider()
        
        st.header("Search Filters")
        n_results = st.slider("Number of Results", 1, 20, 5)
        
        language = st.selectbox(
            "Language",
            ["All", "cpp", "python", "javascript", "mojom", "gn"]
        )
        
        chunk_type = st.selectbox(
            "Type",
            ["All", "function", "class", "method", "struct", "interface"]
        )
        
        st.divider()
        
        if st.button("Refresh Statistics"):
            st.session_state.show_stats = True

    # Initialize System
    try:
        rag = get_rag_system(db_path)
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        return

    # Tabs
    tab_search, tab_symbol, tab_stats = st.tabs(["Semantic Search", "Symbol Lookup", "Statistics"])
    
    # --- Tab 1: Semantic Search ---
    with tab_search:
        query = st.text_input("Search Query", placeholder="e.g., buffer overflow protection in render frame")
        
        if query:
            with st.spinner("Searching..."):
                start_time = time.time()
                
                # Prepare filters
                lang_filter = None if language == "All" else language
                type_filter = None if chunk_type == "All" else chunk_type
                
                results = rag.retrieve_context(
                    query=query,
                    n_results=n_results,
                    language=lang_filter,
                    file_type=type_filter
                )
                
                duration = time.time() - start_time
                st.success(f"Found {len(results)} results in {duration:.3f}s")
                
                for i, result in enumerate(results, 1):
                    meta = result['metadata']
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="result-card">
                            <h3>{i}. {meta.get('name', 'Unknown')}</h3>
                            <p>
                                <span class="metadata-tag">📄 {meta.get('filepath')}</span>
                                <span class="metadata-tag">🏷️ {meta.get('type')}</span>
                                <span class="metadata-tag">💻 {meta.get('language')}</span>
                                <span class="metadata-tag">📊 Similarity: {1 - result['distance']:.3f}</span>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.code(result['content'], language=meta.get('language', 'text'))
                        st.divider()

    # --- Tab 2: Symbol Lookup ---
    with tab_symbol:
        col1, col2 = st.columns([3, 1])
        with col1:
            symbol_name = st.text_input("Symbol Name", placeholder="e.g., RenderFrameHost")
        with col2:
            exact_match = st.checkbox("Exact Match", value=True)
            
        if symbol_name:
            with st.spinner("Looking up symbol..."):
                lang_filter = None if language == "All" else language
                type_filter = None if chunk_type == "All" else chunk_type
                
                results = rag.retrieve_symbol(
                    symbol_name=symbol_name,
                    symbol_type=type_filter,
                    language=lang_filter,
                    n_results=n_results
                )
                
                if not results:
                    st.warning(f"Symbol '{symbol_name}' not found")
                else:
                    st.success(f"Found {len(results)} definitions")
                    
                    for result in results:
                        meta = result['metadata']
                        st.markdown(f"### {meta.get('name')}")
                        st.caption(f"File: {meta.get('filepath')} | Type: {meta.get('type')}")
                        st.code(result['content'], language=meta.get('language', 'text'))
                        st.divider()

    # --- Tab 3: Statistics ---
    with tab_stats:
        if st.button("Load Statistics") or st.session_state.get('show_stats'):
            stats = rag.get_statistics()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Chunks", stats['total_chunks'])
            col2.metric("Unique Files", stats['unique_files'])
            col3.metric("Languages", len(stats['chunks_by_language']))
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("Chunks by Language")
                st.bar_chart(stats['chunks_by_language'])
                
            with col_b:
                st.subheader("Chunks by Type")
                st.bar_chart(stats['chunks_by_type'])

if __name__ == "__main__":
    main()
