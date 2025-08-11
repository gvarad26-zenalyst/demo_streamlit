import streamlit as st
import boto3
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv('config.env')

class S3DataVisualizer:
    def __init__(self):
        """Initialize S3 client with credentials from environment"""
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION')
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
        except Exception as e:
            st.error(f"Failed to initialize S3 client: {str(e)}")
            self.s3_client = None
    
    def list_s3_objects(self, prefix: str = "") -> List[str]:
        """List all JSON objects in the S3 bucket"""
        try:
            if not self.s3_client:
                return []
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            objects = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.endswith('.json'):
                        objects.append(key)
            
            return sorted(objects)
        except Exception as e:
            st.error(f"Error listing S3 objects: {str(e)}")
            return []
    
    def fetch_json_from_s3(self, object_key: str) -> Optional[Dict]:
        """Fetch and parse JSON data from S3"""
        try:
            if not self.s3_client:
                return None
            
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            json_content = response['Body'].read().decode('utf-8')
            return json.loads(json_content)
        
        except Exception as e:
            st.error(f"Error fetching {object_key}: {str(e)}")
            return None
    
    def extract_client_id_from_key(self, object_key: str) -> str:
        """Extract client ID from S3 object key"""
        # Assuming format like "client_123/report.json" or "client_123_report.json"
        if '/' in object_key:
            return object_key.split('/')[0]
        elif '_' in object_key:
            parts = object_key.split('_')
            if len(parts) >= 2:
                return '_'.join(parts[:2])  # client_id format
        return object_key.replace('.json', '')
    
    def create_comprehensive_dashboard(self, json_data: Dict, client_id: str):
        """Create comprehensive dashboard from JSON data"""
        
        st.header(f"📊 Data Analytics Dashboard - {client_id}")
        st.markdown(f"**Data Source:** `s3://{self.bucket_name}`")
        
        # Display analysis metadata if available
        if 'analysis_metadata' in json_data:
            metadata = json_data['analysis_metadata']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Process", metadata.get('process_name', 'N/A'))
            with col2:
                st.metric("Success", "✅ Yes" if metadata.get('success', False) else "❌ No")
            with col3:
                if 'execution_time_seconds' in json_data:
                    st.metric("Execution Time", f"{json_data['execution_time_seconds']:.1f}s")
        
        # Create adaptive tabs based on data structure
        tabs = st.tabs(["📊 Data Overview", "📈 Visualizations", "🔍 Analysis Results", "📋 Raw Data"])
        
        with tabs[0]:  # Data Overview
            self.create_adaptive_overview(json_data, client_id)
        
        with tabs[1]:  # Visualizations
            self.create_adaptive_visualizations(json_data)
        
        with tabs[2]:  # Analysis Results
            self.create_analysis_results_view(json_data)
        
        with tabs[3]:  # Raw Data
            self.display_raw_data(json_data, client_id)
    
    def create_overview_dashboard(self, data: Dict, client_id: str):
        """Create overview dashboard with key metrics"""
        st.subheader("🎯 Key Performance Indicators")
        
        # Extract key metrics
        metrics = self.extract_key_metrics(data)
        
        if metrics:
            # Display metrics in columns
            cols = st.columns(min(4, len(metrics)))
            for i, (key, value) in enumerate(metrics.items()):
                if i < 4:
                    with cols[i]:
                        formatted_value = self.format_metric_value(key, value)
                        st.metric(key.replace('_', ' ').title(), formatted_value)
        
        # Create overview visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Data distribution pie chart
            self.create_data_distribution_chart(data)
        
        with col2:
            # Trend analysis if temporal data exists
            self.create_trend_analysis(data)
    
    def create_detailed_analysis(self, data: Dict, client_id: str):
        """Create detailed analysis visualizations"""
        st.subheader("📊 Detailed Data Analysis")
        
        # Extract numeric data for analysis
        numeric_data = self.extract_numeric_data(data)
        
        if numeric_data:
            # Correlation heatmap
            if len(numeric_data) > 1:
                st.subheader("🔥 Data Correlation Heatmap")
                self.create_correlation_heatmap(numeric_data)
            
            # Distribution plots
            st.subheader("📈 Data Distributions")
            self.create_distribution_plots(numeric_data)
        
        # Text analysis if applicable
        text_data = self.extract_text_data(data)
        if text_data:
            st.subheader("📝 Text Analysis")
            self.create_text_analysis(text_data)
    
    def create_financial_dashboard(self, data: Dict, client_id: str):
        """Create financial-specific dashboard"""
        st.subheader("💰 Financial Analysis")
        
        # Extract financial data
        financial_data = self.extract_financial_data(data)
        
        if financial_data:
            # Financial KPIs
            fin_cols = st.columns(3)
            fin_items = list(financial_data.items())[:3]
            
            for i, (key, value) in enumerate(fin_items):
                with fin_cols[i]:
                    formatted_value = self.format_financial_value(key, value)
                    st.metric(key.replace('_', ' ').title(), formatted_value)
            
            # Financial charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Financial breakdown
                if len(financial_data) > 1:
                    self.create_financial_breakdown_chart(financial_data)
            
            with col2:
                # Financial trends
                self.create_financial_trends(financial_data)
    
    def display_raw_data(self, data: Dict, client_id: str):
        """Display raw data with search and filtering capabilities"""
        st.subheader("📋 Raw Data Explorer")
        
        # Handle analysis_results specifically for HR/payroll data
        analysis_results = data.get('analysis_results', [])
        
        if analysis_results and isinstance(analysis_results, list):
            st.subheader("👥 Employee Data")
            
            try:
                # Convert analysis results to DataFrame
                df = pd.DataFrame(analysis_results)
                
                # Handle NaN values and mixed types
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).replace('nan', 'N/A')
                
                # Search functionality
                search_term = st.text_input("🔍 Search employees:", placeholder="Enter name, department, or designation...")
                
                if search_term:
                    # Filter DataFrame
                    mask = df.astype(str).apply(
                        lambda x: x.str.contains(search_term, case=False, na=False)
                    ).any(axis=1)
                    df = df[mask]
                
                # Display DataFrame with better formatting
                st.dataframe(
                    df.style.format({
                        col: "{:,.0f}" for col in df.columns 
                        if df[col].dtype in ['int64', 'float64'] and 'CTC' in col or 'Pay' in col or 'Allowance' in col
                    }),
                    use_container_width=True, 
                    height=400
                )
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Employee Data CSV",
                        data=csv,
                        file_name=f"{client_id}_employee_data.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    json_str = json.dumps(data, indent=2)
                    st.download_button(
                        "📥 Download Full JSON",
                        data=json_str,
                        file_name=f"{client_id}_analysis.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.warning(f"Could not create employee data table: {str(e)}")
                st.json(analysis_results)
        
        # Show other data sections
        other_data = {k: v for k, v in data.items() if k != 'analysis_results'}
        if other_data:
            with st.expander("📊 Analysis Metadata & Strategy", expanded=False):
                st.json(other_data)
    
    def extract_key_metrics(self, data: Dict) -> Dict:
        """Extract key metrics from data"""
        metrics = {}
        
        def extract_from_dict(d: Dict, prefix: str = ""):
            for key, value in d.items():
                full_key = f"{prefix}_{key}" if prefix else key
                
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    metrics[full_key] = value
                elif isinstance(value, dict):
                    extract_from_dict(value, full_key)
                elif isinstance(value, list) and value:
                    if all(isinstance(item, (int, float)) for item in value):
                        metrics[f"{full_key}_avg"] = np.mean(value)
                        metrics[f"{full_key}_sum"] = sum(value)
        
        extract_from_dict(data)
        return dict(list(metrics.items())[:10])  # Limit to top 10 metrics
    
    def extract_numeric_data(self, data: Dict) -> Dict:
        """Extract all numeric data for analysis"""
        numeric_data = {}
        
        def extract_numeric(d: Dict, prefix: str = ""):
            for key, value in d.items():
                full_key = f"{prefix}_{key}" if prefix else key
                
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    numeric_data[full_key] = value
                elif isinstance(value, dict):
                    extract_numeric(value, full_key)
                elif isinstance(value, list) and value:
                    if all(isinstance(item, (int, float)) for item in value):
                        numeric_data[f"{full_key}_values"] = value
        
        extract_numeric(data)
        return numeric_data
    
    def extract_financial_data(self, data: Dict) -> Dict:
        """Extract financial-specific data"""
        financial_keywords = ['revenue', 'income', 'profit', 'cost', 'expense', 'sales', 
                            'price', 'amount', 'total', 'balance', 'budget', 'roi']
        
        financial_data = {}
        
        def extract_financial(d: Dict, prefix: str = ""):
            for key, value in d.items():
                full_key = f"{prefix}_{key}" if prefix else key
                
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if any(keyword in key.lower() for keyword in financial_keywords):
                        financial_data[full_key] = value
                elif isinstance(value, dict):
                    extract_financial(value, full_key)
        
        extract_financial(data)
        return financial_data
    
    def extract_text_data(self, data: Dict) -> List[str]:
        """Extract text data for analysis"""
        text_data = []
        
        def extract_text(d: Dict):
            for key, value in d.items():
                if isinstance(value, str) and len(value) > 10:  # Meaningful text
                    text_data.append(value)
                elif isinstance(value, dict):
                    extract_text(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and len(item) > 10:
                            text_data.append(item)
                        elif isinstance(item, dict):
                            extract_text(item)
        
        extract_text(data)
        return text_data
    
    def format_metric_value(self, key: str, value: Any) -> str:
        """Format metric values for display"""
        if isinstance(value, (int, float)):
            if abs(value) >= 1000000:
                return f"{value/1000000:.1f}M"
            elif abs(value) >= 1000:
                return f"{value/1000:.1f}K"
            else:
                return f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
        return str(value)
    
    def format_financial_value(self, key: str, value: Any) -> str:
        """Format financial values with currency"""
        if isinstance(value, (int, float)):
            if 'percentage' in key.lower() or 'rate' in key.lower():
                return f"{value:.1f}%"
            else:
                return f"${value:,.0f}"
        return str(value)
    
    def flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def create_data_distribution_chart(self, data: Dict):
        """Create data type distribution pie chart"""
        try:
            type_counts = {}
            
            def count_types(d: Dict):
                for key, value in d.items():
                    value_type = type(value).__name__
                    if isinstance(value, dict):
                        type_counts['nested_object'] = type_counts.get('nested_object', 0) + 1
                        count_types(value)
                    elif isinstance(value, list):
                        type_counts['array'] = type_counts.get('array', 0) + 1
                    else:
                        type_counts[value_type] = type_counts.get(value_type, 0) + 1
            
            count_types(data)
            
            if type_counts:
                fig = px.pie(
                    values=list(type_counts.values()),
                    names=list(type_counts.keys()),
                    title="Data Type Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Could not create distribution chart")
    
    def create_trend_analysis(self, data: Dict):
        """Create trend analysis if temporal data exists"""
        # This is a placeholder - would need actual time series data
        st.info("📈 Trend analysis available when temporal data is present")
    
    def create_correlation_heatmap(self, numeric_data: Dict):
        """Create correlation heatmap"""
        try:
            if len(numeric_data) < 2:
                return
            
            # Convert to DataFrame for correlation
            df_data = {}
            for key, value in numeric_data.items():
                if isinstance(value, list):
                    if len(value) > 1:
                        df_data[key] = value
                else:
                    df_data[key] = [value]  # Single value
            
            if df_data:
                # Ensure all arrays have the same length
                max_len = max(len(v) if isinstance(v, list) else 1 for v in df_data.values())
                for key in df_data:
                    if isinstance(df_data[key], list):
                        while len(df_data[key]) < max_len:
                            df_data[key].append(df_data[key][-1])  # Repeat last value
                    else:
                        df_data[key] = [df_data[key]] * max_len
                
                df = pd.DataFrame(df_data)
                corr_matrix = df.corr()
                
                fig = px.imshow(
                    corr_matrix,
                    labels=dict(color="Correlation"),
                    title="Data Correlation Matrix"
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Could not create correlation heatmap")
    
    def create_distribution_plots(self, numeric_data: Dict):
        """Create distribution plots for numeric data"""
        try:
            # Show top 6 numeric variables
            items = list(numeric_data.items())[:6]
            
            if len(items) >= 2:
                cols = st.columns(2)
                for i, (key, value) in enumerate(items):
                    with cols[i % 2]:
                        if isinstance(value, list) and len(value) > 1:
                            fig = px.histogram(
                                x=value,
                                title=f"Distribution: {key.replace('_', ' ').title()}"
                            )
                            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Could not create distribution plots")
    
    def create_text_analysis(self, text_data: List[str]):
        """Create text analysis visualization"""
        if text_data:
            # Word count analysis
            all_text = ' '.join(text_data)
            words = all_text.lower().split()
            word_counts = {}
            
            for word in words:
                if len(word) > 3:  # Filter short words
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            # Top 10 words
            top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if top_words:
                fig = px.bar(
                    x=[word for word, count in top_words],
                    y=[count for word, count in top_words],
                    title="Top 10 Most Frequent Words"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def create_financial_breakdown_chart(self, financial_data: Dict):
        """Create financial breakdown pie chart"""
        try:
            # Use absolute values for pie chart
            pie_data = {k: abs(v) for k, v in financial_data.items() if v != 0}
            
            if pie_data:
                fig = px.pie(
                    values=list(pie_data.values()),
                    names=[k.replace('_', ' ').title() for k in pie_data.keys()],
                    title="Financial Breakdown"
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Could not create financial breakdown chart")
    
    def create_financial_trends(self, financial_data: Dict):
        """Create financial trends visualization"""
        # Placeholder for trend analysis
        st.info("📈 Financial trends available with time-series data")
    
    def create_adaptive_overview(self, data: Dict, client_id: str):
        """Create adaptive overview based on data structure"""
        st.subheader("🎯 Data Structure Overview")
        
        # Analyze data structure
        structure_info = self.analyze_data_structure(data)
        
        # Display structure metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Keys", structure_info['total_keys'])
        with col2:
            st.metric("Nested Objects", structure_info['nested_objects'])
        with col3:
            st.metric("Arrays", structure_info['arrays'])
        with col4:
            st.metric("Numeric Fields", structure_info['numeric_fields'])
        
        # Data type distribution
        if structure_info['type_distribution']:
            fig = px.pie(
                values=list(structure_info['type_distribution'].values()),
                names=list(structure_info['type_distribution'].keys()),
                title="Data Type Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Show key sections
        st.subheader("📋 Main Data Sections")
        for key, value in data.items():
            if isinstance(value, dict):
                st.write(f"**{key}**: {len(value)} fields")
            elif isinstance(value, list):
                st.write(f"**{key}**: {len(value)} items")
            else:
                st.write(f"**{key}**: {type(value).__name__}")
    
    def create_adaptive_visualizations(self, data: Dict):
        """Create visualizations based on actual data content"""
        st.subheader("📈 Adaptive Data Visualizations")
        
        # Handle analysis_results if present (like your JSON examples)
        if 'analysis_results' in data and isinstance(data['analysis_results'], list):
            analysis_results = data['analysis_results']
            if analysis_results:
                self.visualize_analysis_results(analysis_results)
        
        # Handle strategy information
        if 'strategy_used' in data or 'strategy' in data:
            self.visualize_strategy_info(data)
        
        # Handle execution results
        if 'execution_results' in data:
            self.visualize_execution_info(data['execution_results'])
        
        # Handle recommendations
        if 'recommendations' in data:
            self.visualize_recommendations(data['recommendations'])
        
        # Generic numeric data visualization
        numeric_data = self.extract_all_numeric_data(data)
        if numeric_data:
            self.create_generic_numeric_visualizations(numeric_data)
    
    def create_analysis_results_view(self, data: Dict):
        """Create detailed view of analysis results"""
        st.subheader("🔍 Analysis Results Deep Dive")
        
        # Show analysis metadata
        if 'analysis_metadata' in data:
            st.subheader("📊 Analysis Information")
            metadata = data['analysis_metadata']
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Process Name:**", metadata.get('process_name', 'N/A'))
                st.write("**Success:**", metadata.get('success', False))
            with col2:
                st.write("**Timestamp:**", metadata.get('generation_timestamp', 'N/A'))
                if 'execution_time_seconds' in data:
                    st.write("**Execution Time:**", f"{data['execution_time_seconds']:.2f} seconds")
        
        # Show strategy information
        if 'strategy_used' in data:
            with st.expander("🎯 Strategy Details", expanded=False):
                strategy = data['strategy_used']
                if 'available_columns' in strategy:
                    st.write("**Available Columns:**")
                    cols = st.columns(3)
                    for i, col in enumerate(strategy['available_columns']):
                        with cols[i % 3]:
                            st.write(f"• {col}")
        
        # Show recommendations
        if 'recommendations' in data and data['recommendations']:
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(data['recommendations'], 1):
                st.write(f"{i}. {rec}")
        
        # Show data insights
        if 'data_insights' in data and data['data_insights']:
            st.subheader("🔍 Data Insights")
            for insight in data['data_insights']:
                st.info(insight)
    
    def analyze_data_structure(self, data: Dict) -> Dict:
        """Analyze the structure of JSON data"""
        structure_info = {
            'total_keys': 0,
            'nested_objects': 0,
            'arrays': 0,
            'numeric_fields': 0,
            'type_distribution': {}
        }
        
        def analyze_recursive(obj, depth=0):
            if isinstance(obj, dict):
                structure_info['total_keys'] += len(obj)
                if depth > 0:
                    structure_info['nested_objects'] += 1
                
                for key, value in obj.items():
                    value_type = type(value).__name__
                    structure_info['type_distribution'][value_type] = structure_info['type_distribution'].get(value_type, 0) + 1
                    
                    if isinstance(value, (int, float)):
                        structure_info['numeric_fields'] += 1
                    elif isinstance(value, list):
                        structure_info['arrays'] += 1
                    elif isinstance(value, dict):
                        analyze_recursive(value, depth + 1)
                        
            elif isinstance(obj, list):
                structure_info['arrays'] += 1
                for item in obj:
                    if isinstance(item, dict):
                        analyze_recursive(item, depth + 1)
        
        analyze_recursive(data)
        return structure_info
    
    def visualize_analysis_results(self, analysis_results: List[Dict]):
        """Visualize analysis results data"""
        try:
            df = pd.DataFrame(analysis_results)
            
            # Clean data types to avoid PyArrow errors
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Convert to string and handle NaN
                    df[col] = df[col].astype(str).replace('nan', '')
            
            st.subheader("📊 Analysis Results Overview")
            st.write(f"**Total Records:** {len(df)}")
            
            # Show column info
            col_info = []
            for col in df.columns:
                col_info.append({
                    'Column': col,
                    'Type': str(df[col].dtype),
                    'Non-null': df[col].count(),
                    'Unique': df[col].nunique()
                })
            
            col_df = pd.DataFrame(col_info)
            st.dataframe(col_df, use_container_width=True)
            
            # Create visualizations based on data types
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) > 0:
                st.subheader("📈 Numeric Data Distribution")
                
                # Show up to 4 numeric columns
                cols_to_show = list(numeric_cols)[:4]
                fig_cols = st.columns(min(2, len(cols_to_show)))
                
                for i, col in enumerate(cols_to_show):
                    with fig_cols[i % 2]:
                        fig = px.histogram(df, x=col, title=f"Distribution of {col}")
                        st.plotly_chart(fig, use_container_width=True)
            
            if len(categorical_cols) > 0:
                st.subheader("📊 Categorical Data Analysis")
                
                # Show value counts for categorical columns
                for col in list(categorical_cols)[:3]:  # Limit to 3 columns
                    if df[col].nunique() < 20:  # Only if not too many unique values
                        value_counts = df[col].value_counts()
                        if len(value_counts) > 1:
                            fig = px.bar(
                                x=value_counts.index,
                                y=value_counts.values,
                                title=f"Distribution of {col}"
                            )
                            st.plotly_chart(fig, use_container_width=True)
            
            # Correlation heatmap for numeric data
            if len(numeric_cols) > 1:
                st.subheader("🔥 Correlation Analysis")
                corr_matrix = df[numeric_cols].corr()
                fig = px.imshow(
                    corr_matrix,
                    labels=dict(color="Correlation"),
                    title="Correlation Matrix"
                )
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.warning(f"Could not create visualizations: {str(e)}")
            st.info("Data structure may not be suitable for standard visualizations")
    
    def visualize_strategy_info(self, data: Dict):
        """Visualize strategy information"""
        strategy = data.get('strategy_used', data.get('strategy', {}))
        
        if 'available_columns' in strategy:
            st.subheader("📋 Available Data Columns")
            columns = strategy['available_columns']
            
            # Create a simple bar chart of column count by type (if we can infer types)
            if len(columns) > 0:
                st.write(f"**Total Columns:** {len(columns)}")
                
                # Display columns in a nice format
                cols_per_row = 3
                for i in range(0, len(columns), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col_name in enumerate(columns[i:i+cols_per_row]):
                        with cols[j]:
                            st.write(f"• {col_name}")
    
    def visualize_execution_info(self, execution_results: Dict):
        """Visualize execution information"""
        st.subheader("⚙️ Execution Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Success:**", "✅ Yes" if execution_results.get('success', False) else "❌ No")
        with col2:
            if execution_results.get('stdout'):
                st.write("**Output Available:**", "✅ Yes")
            if execution_results.get('stderr'):
                st.write("**Errors:**", "⚠️ Present")
    
    def visualize_recommendations(self, recommendations: List[str]):
        """Visualize recommendations"""
        if recommendations:
            st.subheader("💡 Key Recommendations")
            
            # Categorize recommendations
            categories = {
                'Data Quality': [],
                'Analysis': [],
                'Review': [],
                'Other': []
            }
            
            for rec in recommendations:
                if any(word in rec.lower() for word in ['data quality', 'quality', 'completeness']):
                    categories['Data Quality'].append(rec)
                elif any(word in rec.lower() for word in ['analysis', 'analyze', 'comprehensive']):
                    categories['Analysis'].append(rec)
                elif any(word in rec.lower() for word in ['review', 'validate', 'check']):
                    categories['Review'].append(rec)
                else:
                    categories['Other'].append(rec)
            
            # Display categorized recommendations
            for category, recs in categories.items():
                if recs:
                    st.write(f"**{category}:**")
                    for rec in recs:
                        st.write(f"• {rec}")
    
    def extract_all_numeric_data(self, data: Dict) -> Dict:
        """Extract all numeric data from nested JSON"""
        numeric_data = {}
        
        def extract_recursive(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full_key = f"{prefix}_{key}" if prefix else key
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        numeric_data[full_key] = value
                    elif isinstance(value, dict):
                        extract_recursive(value, full_key)
                    elif isinstance(value, list) and value:
                        if all(isinstance(item, (int, float)) for item in value):
                            numeric_data[f"{full_key}_avg"] = np.mean(value)
                            numeric_data[f"{full_key}_sum"] = sum(value)
        
        extract_recursive(data)
        return numeric_data
    
    def create_generic_numeric_visualizations(self, numeric_data: Dict):
        """Create generic visualizations for numeric data"""
        if len(numeric_data) > 1:
            st.subheader("📊 Numeric Data Overview")
            
            # Bar chart of all numeric values
            if len(numeric_data) <= 10:  # Only if not too many values
                fig = px.bar(
                    x=list(numeric_data.keys()),
                    y=list(numeric_data.values()),
                    title="Numeric Values Overview"
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
