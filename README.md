# 📊 Excel Analysis Dashboard

A **LLM-powered Excel analysis platform** built with Streamlit, designed for maximum parallel report generation. This application provides comprehensive Excel file analysis capabilities for both investors and investees.

## 🚀 Features

- **🔐 Secure Authentication**: Role-based access control (Investor/Investee)
- **📤 Multi-file Upload**: Upload multiple Excel files simultaneously
- **🤖 LLM Analysis**: AI-powered Excel data analysis and insights
- **📊 Interactive Dashboards**: Comprehensive data visualization
- **☁️ S3 Integration**: Direct S3 data access and visualization
- **🔄 Real-time Status**: Monitor analysis progress in real-time
- **📈 Parallel Processing**: Maximum parallel report generation
- **🎯 Role-specific Views**: Different dashboards for different user roles

## 🏗️ Architecture

- **Frontend**: Streamlit web application
- **Backend**: External API server (FastAPI/Uvicorn)
- **Storage**: AWS S3 for data persistence
- **Authentication**: Local session-based authentication
- **Data Processing**: LLM-powered analysis engine

## 🔧 Setup Instructions

### Prerequisites
- Python 3.8+
- pip package manager
- AWS S3 bucket and credentials
- External API server running

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Streamlit_demo
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy the example configuration
cp config.env.example config.env

# Edit config.env with your actual values
nano config.env  # or use your preferred editor
```

**Required Environment Variables:**
- `S3_BUCKET_NAME`: Your S3 bucket name
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_REGION`: Your AWS region
- `API_BASE_URL`: Your API server URL

### 4. Run the Application
```bash
python run_excel_analysis.py
```

Or directly with Streamlit:
```bash
streamlit run main_app.py
```

## 🔐 Security Notes

⚠️ **IMPORTANT**: This repository contains NO sensitive information:
- ✅ No AWS credentials
- ✅ No real IP addresses
- ✅ No user passwords
- ✅ No session tokens
- ✅ No S3 bucket names

All sensitive data has been replaced with placeholder values. Users must configure their own:
- API server URLs
- AWS credentials
- S3 bucket names
- Database connections

## 📁 Project Structure

```
Streamlit_demo/
├── main_app.py              # Main application entry point
├── auth.py                  # Authentication system
├── excel_analysis_ui.py     # Main UI components
├── s3_data_visualizer.py    # S3 data visualization
├── run_excel_analysis.py    # Launch script
├── requirements.txt          # Python dependencies
├── config.env.example       # Configuration template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 API Configuration

**Base URL**: `http://your-api-server:8006` (Replace with your actual API server URL)

**Endpoints**:
- `GET /health` - Health check
- `GET /test-s3` - S3 connection test
- `POST /upload-and-analyze` - File upload and analysis
- `GET /status/{session_id}` - Analysis status
- `GET /dashboard/{client_id}` - Client dashboard

## 🎭 User Roles

### Investor Role
- Upload Excel files for investment analysis
- View comprehensive investment reports
- Access multiple client dashboards
- Generate investment recommendations

### Investee Role
- Upload business Excel files for analysis
- View business performance insights
- Access investment readiness reports
- Track business metrics

## 🚀 Deployment

### Local Development
```bash
streamlit run main_app.py --server.port 8501
```

### Production Deployment
1. Set up environment variables
2. Configure reverse proxy (nginx)
3. Use process manager (systemd, PM2)
4. Enable HTTPS with SSL certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the configuration examples

---

**Built with ❤️ using Streamlit, Python, and AWS S3**