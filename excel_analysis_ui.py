import streamlit as st
import requests
import json
import time
from typing import Optional, Dict, Any, List
import pandas as pd
from datetime import datetime
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from auth import check_authentication, show_login_page, logout_user, get_current_user, get_current_client_id
from s3_data_visualizer import S3DataVisualizer

# Configure Streamlit page
st.set_page_config(
    page_title="Excel Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://13.60.4.11:8006"

class ExcelAnalysisAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    def health_check(self) -> Dict:
        """Check API health status"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def test_s3_connection(self) -> Dict:
        """Test S3 connection"""
        try:
            response = requests.get(f"{self.base_url}/test-s3", timeout=30)
            return {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def upload_and_analyze(self, client_id: str, files: list) -> Dict:
        """Upload Excel files and start analysis"""
        try:
            # Prepare files for upload
            files_data = []
            for file in files:
                files_data.append(('files', (file.name, file.getvalue(), file.type)))
            
            # Prepare form data
            data = {'client_id': client_id}
            
            # Remove timeout to let the analysis run as long as needed
            response = requests.post(
                f"{self.base_url}/upload-and-analyze",
                data=data,
                files=files_data
            )
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def get_analysis_status(self, session_id: str) -> Dict:
        """Get analysis status by session ID"""
        try:
            response = requests.get(f"{self.base_url}/status/{session_id}", timeout=30)
            return {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def get_client_dashboard(self, client_id: str) -> Dict:
        """Get client dashboard data"""
        try:
            response = requests.get(f"{self.base_url}/dashboard/{client_id}", timeout=30)
            return {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}

def display_response(response_data: Dict, title: str = "Response"):
    """Display API response in a formatted way"""
    st.subheader(f"📋 {title}")
    
    if response_data["status"] == "success":
        st.success(f"✅ Success (Status: {response_data.get('status_code', 'N/A')})")
        
        # Display response data
        if isinstance(response_data["data"], dict):
            # Show key metrics first if available
            data = response_data["data"]
            
            # Create metrics row for key information
            if any(key in data for key in ["session_id", "client_id", "status", "message"]):
                cols = st.columns(4)
                col_idx = 0
                
                if "session_id" in data and col_idx < 4:
                    with cols[col_idx]:
                        st.metric("🆔 Session ID", data["session_id"][:8] + "...")
                        col_idx += 1
                
                if "client_id" in data and col_idx < 4:
                    with cols[col_idx]:
                        st.metric("👤 Client ID", data["client_id"])
                        col_idx += 1
                
                if "status" in data and col_idx < 4:
                    with cols[col_idx]:
                        st.metric("📊 Status", data["status"])
                        col_idx += 1
                
                if "files_processed" in data and col_idx < 4:
                    with cols[col_idx]:
                        st.metric("📁 Files", data["files_processed"])
                        col_idx += 1
            
            # Show full response in expandable section
            with st.expander("🔍 Full Response Details", expanded=False):
                st.json(response_data["data"])
            
            # If it's a list, also show as table
            if isinstance(response_data["data"], list) and response_data["data"]:
                try:
                    df = pd.DataFrame(response_data["data"])
                    st.subheader("📊 Data Table")
                    st.dataframe(df, use_container_width=True)
                except:
                    pass
        else:
            st.code(str(response_data["data"]))
    else:
        st.error(f"❌ Error (Status: {response_data.get('status_code', 'N/A')})")
        if "error" in response_data:
            st.error(f"Error: {response_data['error']}")
        if "data" in response_data:
            st.code(str(response_data["data"]))

def create_dashboard_visualizations(dashboard_data: Dict, client_id: str, user_role: str):
    """Create comprehensive dashboard visualizations based on the data structure"""
    
    st.divider()
    st.header("📊 Interactive Dashboard")
    st.markdown(f"**Client ID:** `{client_id}` | **Role:** {user_role.title()}")
    
    # Extract different types of data from the dashboard
    reports = dashboard_data.get('reports', [])
    summary_stats = dashboard_data.get('summary', {})
    analysis_results = dashboard_data.get('analysis_results', {})
    
    # Create tabs for different visualization categories
    viz_tabs = st.tabs(["📈 Overview", "📋 Data Tables"])
    
    with viz_tabs[0]:  # Overview Tab
        st.subheader("🎯 Key Performance Indicators")
        
        # Create KPI metrics from summary stats
        if summary_stats:
            kpi_cols = st.columns(4)
            kpi_items = list(summary_stats.items())
            
            for i, (key, value) in enumerate(kpi_items[:4]):
                with kpi_cols[i]:
                    if isinstance(value, (int, float)):
                        # Format the value based on its magnitude
                        if abs(value) >= 1000000:
                            formatted_value = f"{value/1000000:.1f}M"
                        elif abs(value) >= 1000:
                            formatted_value = f"{value/1000:.1f}K"
                        else:
                            formatted_value = f"{value:,.2f}" if isinstance(value, float) else str(value)
                        
                        st.metric(
                            key.replace('_', ' ').title(),
                            formatted_value,
                            delta=None
                        )
                    else:
                        st.metric(key.replace('_', ' ').title(), str(value))
        
        # Overview charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Reports overview pie chart
            if reports and isinstance(reports, list):
                st.subheader("📊 Reports Distribution")
                
                # Count reports by type or status
                report_types = {}
                for report in reports:
                    if isinstance(report, dict):
                        report_type = report.get('type', report.get('category', 'General'))
                        report_types[report_type] = report_types.get(report_type, 0) + 1
                
                if report_types:
                    fig_pie = px.pie(
                        values=list(report_types.values()),
                        names=list(report_types.keys()),
                        title="Report Types Distribution"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Summary statistics bar chart
            if summary_stats:
                st.subheader("📈 Summary Statistics")
                
                numeric_stats = {k: v for k, v in summary_stats.items() 
                               if isinstance(v, (int, float))}
                
                if numeric_stats:
                    fig_bar = px.bar(
                        x=list(numeric_stats.keys()),
                        y=list(numeric_stats.values()),
                        title="Key Metrics Overview"
                    )
                    fig_bar.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)
    
    with viz_tabs[1]:  # Data Tables Tab
        st.subheader("📋 Detailed Data Tables")
        
        # Reports table
        if reports and isinstance(reports, list):
            st.subheader("📊 Reports Data")
            
            # Convert reports to DataFrame
            try:
                if all(isinstance(report, dict) for report in reports):
                    df_reports = pd.DataFrame(reports)
                    
                    # Add search functionality
                    search_term = st.text_input("🔍 Search in reports:", placeholder="Enter search term...")
                    
                    if search_term:
                        # Filter DataFrame based on search term
                        mask = df_reports.astype(str).apply(
                            lambda x: x.str.contains(search_term, case=False, na=False)
                        ).any(axis=1)
                        df_reports = df_reports[mask]
                    
                    # Display with pagination
                    st.dataframe(
                        df_reports,
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download button
                    csv = df_reports.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Reports CSV",
                        data=csv,
                        file_name=f"{client_id}_reports.csv",
                        mime="text/csv"
                    )
                else:
                    st.write("Reports data (raw format):")
                    st.json(reports)
                    
            except Exception as e:
                st.warning(f"Could not create reports table: {str(e)}")
                st.json(reports)
        
        # Summary statistics table
        if summary_stats:
            st.subheader("📈 Summary Statistics")
            df_summary = pd.DataFrame(list(summary_stats.items()), columns=['Metric', 'Value'])
            st.dataframe(df_summary, use_container_width=True)
        
        # Analysis results table
        if analysis_results:
            st.subheader("🔍 Analysis Results")
            df_analysis = pd.DataFrame(list(analysis_results.items()), columns=['Analysis Item', 'Result'])
            st.dataframe(df_analysis, use_container_width=True)
        
        # Raw data section
        with st.expander("🔍 Raw Dashboard Data", expanded=False):
            st.json(dashboard_data)

def main():
    # Check authentication first
    if not check_authentication():
        show_login_page()
        return
    
    # Get current user info
    current_user = get_current_user()
    current_client_id = get_current_client_id()
    
    st.title("📊 Excel Analysis Dashboard")
    st.markdown("**LLM-powered Excel analysis with maximum parallel report generation**")
    
    # User info header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"👋 Welcome, **{current_user['full_name']}** ({current_user['role'].title()})")
        st.markdown(f"🆔 Client ID: **{current_client_id}**")
    with col2:
        st.markdown(f"🔗 **API:** `{API_BASE_URL}`")
    with col3:
        if st.button("🚪 Logout", type="secondary"):
            logout_user()
    
    # Initialize API client
    if 'api_client' not in st.session_state:
        st.session_state.api_client = ExcelAnalysisAPI(API_BASE_URL)
    
    api = st.session_state.api_client
    
    # Sidebar for system status
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Health Check
        if st.button("🏥 Health Check", type="secondary"):
            with st.spinner("Checking API health..."):
                health_result = api.health_check()
                if health_result["status"] == "success":
                    st.success("✅ API is healthy!")
                else:
                    st.error("❌ API health check failed")
                st.json(health_result)
        
        # S3 Connection Test
        if st.button("☁️ Test S3 Connection", type="secondary"):
            with st.spinner("Testing S3 connection..."):
                s3_result = api.test_s3_connection()
                if s3_result["status"] == "success":
                    st.success("✅ S3 connection OK!")
                else:
                    st.error("❌ S3 connection failed")
                st.json(s3_result)
        
        st.divider()
        
        # Quick Status Check
        st.subheader("📊 Quick Status")
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Upload & Analyze", 
        "📈 Analysis Status", 
        "📋 Client Dashboard", 
        "☁️ S3 Data Explorer",
        "🧪 API Testing"
    ])
    
    # Tab 1: Upload and Analyze
    with tab1:
        st.header("📤 Upload Excel Files for Analysis")
        st.markdown("Upload one or more Excel files to automatically generate analysis reports with maximum parallel processing.")
        
        # Client ID input (auto-filled from authentication)
        client_id = st.text_input(
            "👤 Client ID", 
            value=current_client_id,
            disabled=True,
            help=f"Your authenticated client ID ({current_user['role']})"
        )
        
        # File upload
        uploaded_files = st.file_uploader(
            "📁 Choose Excel files",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            help="Upload one or more Excel files for analysis"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) selected:")
            for file in uploaded_files:
                file_size = len(file.getvalue()) / 1024  # Size in KB
                st.write(f"- **{file.name}** ({file_size:.1f} KB)")
        
        # Role-specific messaging
        if current_user['role'] == 'investor':
            st.info("🏦 **Investor Mode**: Upload Excel files to analyze investment opportunities and generate comprehensive reports.")
        else:
            st.info("🏢 **Investee Mode**: Upload your business Excel files for analysis to attract potential investors.")
        
        # Upload and analyze button
        if st.button("🚀 Upload & Start Analysis", type="primary", disabled=not uploaded_files):
            if uploaded_files:
                # Create a placeholder for progress updates
                progress_placeholder = st.empty()
                result_placeholder = st.empty()
                
                with progress_placeholder:
                    st.info("📤 Uploading files...")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Update progress
                    progress_bar.progress(25)
                    status_text.text("🔄 Processing files and starting analysis...")
                    
                    # Make the request without timeout
                    result = api.upload_and_analyze(client_id, uploaded_files)
                    
                    # Update progress
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis completed!")
                
                # Clear progress and show results
                progress_placeholder.empty()
                
                with result_placeholder:
                    display_response(result, "Upload & Analysis Result")
                    
                    # Store session info for later use
                    if result["status"] == "success" and "data" in result:
                        if isinstance(result["data"], dict) and "session_id" in result["data"]:
                            st.session_state.last_session_id = result["data"]["session_id"]
                            st.success(f"💡 Session ID saved: {result['data']['session_id']}")
                        
                        # Show success message with details
                        if isinstance(result["data"], dict):
                            st.balloons()  # Celebration animation
                            
                            # Show key information from the response
                            if "reports_generated" in result["data"]:
                                st.metric("📊 Reports Generated", result["data"]["reports_generated"])
                            if "processing_time" in result["data"]:
                                st.metric("⏱️ Processing Time", f"{result['data']['processing_time']:.2f}s")
                            if "files_processed" in result["data"]:
                                st.metric("📁 Files Processed", result["data"]["files_processed"])
            else:
                st.warning("⚠️ Please upload at least one Excel file.")
    
    # Tab 2: Analysis Status
    with tab2:
        st.header("📈 Check Analysis Status")
        st.markdown("Monitor the progress of your analysis and report generation.")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            session_id = st.text_input(
                "🔍 Session ID", 
                value=st.session_state.get('last_session_id', ''),
                placeholder="Enter session ID from upload response",
                help="Session ID returned from the upload & analyze request"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            auto_refresh = st.checkbox("🔄 Auto-refresh", help="Automatically refresh status every 10 seconds")
        
        if st.button("📊 Check Status", type="primary", disabled=not session_id):
            if session_id:
                with st.spinner("Fetching analysis status..."):
                    result = api.get_analysis_status(session_id)
                    display_response(result, "Analysis Status")
            else:
                st.warning("⚠️ Please enter a session ID.")
        
        # Auto-refresh functionality
        if auto_refresh and session_id:
            time.sleep(10)
            st.rerun()
    
    # Tab 3: Client Dashboard
    with tab3:
        st.header("📋 Client Dashboard")
        st.markdown("View comprehensive dashboard data for a specific client.")
        
        # For investors, allow viewing any client's dashboard
        # For investees, only allow viewing their own dashboard
        if current_user['role'] == 'investor':
            dashboard_client_id = st.text_input(
                "👤 Client ID for Dashboard", 
                value=current_client_id,
                placeholder="Enter any client ID to view dashboard",
                help="As an investor, you can view any client's dashboard"
            )
        else:
            dashboard_client_id = st.text_input(
                "👤 Client ID for Dashboard", 
                value=current_client_id,
                disabled=True,
                help="As an investee, you can only view your own dashboard"
            )
        
        if st.button("📊 Load Dashboard", type="primary", disabled=not dashboard_client_id):
            if dashboard_client_id:
                with st.spinner("Loading dashboard data..."):
                    result = api.get_client_dashboard(dashboard_client_id)
                    display_response(result, "Client Dashboard Data")
                    
                    # If successful, create comprehensive visualizations
                    if result["status"] == "success" and isinstance(result["data"], dict):
                        create_dashboard_visualizations(result["data"], dashboard_client_id, current_user['role'])
            else:
                st.warning("⚠️ Please enter a client ID.")
    
    # Tab 4: S3 Data Explorer
    with tab4:
        st.header("☁️ S3 Data Explorer & Visualizer")
        st.markdown("**Direct access to S3 bucket data with advanced visualizations**")
        
        # Initialize S3 visualizer
        if 's3_visualizer' not in st.session_state:
            st.session_state.s3_visualizer = S3DataVisualizer()
        
        s3_viz = st.session_state.s3_visualizer
        
        # Check S3 connection
        if not s3_viz.s3_client:
            st.error("❌ Could not connect to S3. Please check your credentials in config.env")
            st.info("📋 Required environment variables:")
            st.code("""
S3_BUCKET_NAME=final-json-report
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-2
            """)
        else:
            st.success("✅ Connected to S3 successfully!")
            
            # List available objects
            with st.spinner("📋 Loading S3 objects..."):
                s3_objects = s3_viz.list_s3_objects()
            
            if s3_objects:
                st.subheader(f"📁 Available Data Files ({len(s3_objects)} files)")
                
                # Group objects by client ID
                client_groups = {}
                for obj in s3_objects:
                    client_id = s3_viz.extract_client_id_from_key(obj)
                    if client_id not in client_groups:
                        client_groups[client_id] = []
                    client_groups[client_id].append(obj)
                
                # Client selection
                selected_client = st.selectbox(
                    "👤 Select Client:",
                    options=list(client_groups.keys()),
                    help="Choose a client to visualize their data"
                )
                
                if selected_client:
                    client_files = client_groups[selected_client]
                    
                    # File selection
                    selected_file = st.selectbox(
                        "📄 Select Data File:",
                        options=client_files,
                        help="Choose a specific JSON file to visualize"
                    )
                    
                    if selected_file:
                        # Load and visualize button
                        if st.button("🚀 Load & Visualize Data", type="primary"):
                            with st.spinner(f"📊 Loading and analyzing {selected_file}..."):
                                # Fetch data from S3
                                json_data = s3_viz.fetch_json_from_s3(selected_file)
                                
                                if json_data:
                                    st.success(f"✅ Successfully loaded {selected_file}")
                                    
                                    # Create comprehensive dashboard
                                    s3_viz.create_comprehensive_dashboard(json_data, selected_client)
                                else:
                                    st.error("❌ Failed to load data from S3")
                        
                        # Show file info
                        st.info(f"📋 **File:** `{selected_file}` | **Client:** `{selected_client}`")
                
                # Bulk analysis option
                st.divider()
                st.subheader("📊 Bulk Analysis")
                
                if st.button("📈 Analyze All Client Data", type="secondary"):
                    with st.spinner("📊 Performing bulk analysis..."):
                        # Analyze data for current user's client ID
                        user_client_files = client_groups.get(get_current_client_id(), [])
                        
                        if user_client_files:
                            for file in user_client_files[:3]:  # Limit to 3 files
                                st.subheader(f"📄 Analysis: {file}")
                                json_data = s3_viz.fetch_json_from_s3(file)
                                if json_data:
                                    # Create mini dashboard for each file
                                    with st.expander(f"📊 {file} Dashboard", expanded=False):
                                        s3_viz.create_comprehensive_dashboard(json_data, get_current_client_id())
                        else:
                            st.warning(f"No data files found for your client ID: {get_current_client_id()}")
            
            else:
                st.warning("📁 No JSON files found in the S3 bucket")
                st.info("🔍 Make sure your S3 bucket contains JSON files with analysis results")
    
    # Tab 5: API Testing
    with tab5:
        st.header("🧪 API Testing & Diagnostics")
        st.markdown("Test individual API endpoints and view raw responses.")
        
        # Root endpoint test
        st.subheader("🏠 Root Endpoint Test")
        if st.button("Test Root Endpoint (GET /)"):
            try:
                response = requests.get(f"{API_BASE_URL}/", timeout=10)
                st.code(f"Status: {response.status_code}")
                if response.status_code == 200:
                    try:
                        st.json(response.json())
                    except:
                        st.text(response.text)
                else:
                    st.text(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
        
        st.divider()
        
        # Manual endpoint testing
        st.subheader("🔧 Manual Endpoint Testing")
        
        test_endpoint = st.selectbox(
            "Select Endpoint",
            [
                "GET /health",
                "GET /test-s3", 
                "GET /status/{session_id}",
                "GET /dashboard/{client_id}"
            ]
        )
        
        # Parameter input based on selected endpoint
        params = {}
        if "{session_id}" in test_endpoint:
            params["session_id"] = st.text_input("Session ID", key="test_session_id")
        elif "{client_id}" in test_endpoint:
            params["client_id"] = st.text_input("Client ID", key="test_client_id")
        
        if st.button("🚀 Execute Test Request"):
            try:
                # Build URL
                url = API_BASE_URL + test_endpoint.split(" ")[1]
                for param, value in params.items():
                    url = url.replace(f"{{{param}}}", str(value))
                
                # Make request
                response = requests.get(url, timeout=30)
                
                # Display response
                st.code(f"URL: {url}")
                st.code(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        st.json(response.json())
                    except:
                        st.text(response.text)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"Request failed: {e}")
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            📊 Excel Analysis Dashboard | LLM-powered analysis with maximum parallel processing<br>
            🔗 API: http://13.60.4.11:8006 | 🚀 Built with Streamlit
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
