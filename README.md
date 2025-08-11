# 🔐 Excel Analysis Platform

A comprehensive Streamlit application with role-based authentication for **Investors** and **Investees** to analyze Excel files using LLM-powered analysis.

## 🎭 User Roles

### 🏦 **Investor**
- **Client ID Format**: `INV_XXXXXX_YYYYMMDD`
- Upload Excel files for investment analysis
- View any client's dashboard
- Full access to all features

### 🏢 **Investee** 
- **Client ID Format**: `IVE_XXXXXX_YYYYMMDD`
- Upload business Excel files for analysis
- View only their own dashboard
- Seek investment opportunities

## 🚀 Quick Start

### 1. **Installation**
```bash
pip install -r requirements.txt
```

### 2. **Run the Application**
```bash
python run_excel_analysis.py
```

### 3. **Access & Login**
- Open browser to `http://localhost:8501`
- Click **"🎯 Demo Login"** for instant access
- Or register/login with your credentials

## 🎯 Demo Accounts

**Demo Login** creates these accounts automatically:
- **Investor**: `demo_investor` / `demo123`
- **Investee**: `demo_investee` / `demo123`

## 📊 Main Features

### **📤 Upload & Analyze**
- Multi-file Excel upload
- Auto-generated client IDs
- Role-specific guidance
- Progress tracking

### **📈 Analysis Status**
- Real-time progress monitoring
- Session-based tracking
- Auto-refresh functionality

### **📋 Client Dashboard**
- **Investors**: View any client data
- **Investees**: View own data only
- Automatic visualizations
- Key metrics display

### **🔐 Authentication**
- Secure login system
- Role-based access control
- 24-hour sessions
- Automatic client ID generation

## 🗃️ Essential Files

```
📁 Project/
├── 📄 main_app.py              # Main entry point
├── 📄 auth.py                  # Authentication system
├── 📄 excel_analysis_ui.py     # Dashboard UI
├── 📄 run_excel_analysis.py    # Launcher
├── 📄 requirements.txt         # Dependencies
└── 📄 README.md               # Documentation
```

## 🔧 API Configuration

**Base URL**: `http://13.60.4.11:8006`

**Endpoints**:
- `POST /upload-and-analyze` - File upload
- `GET /status/{session_id}` - Progress tracking
- `GET /dashboard/{client_id}` - Dashboard data
- `GET /health` - Health check
- `GET /test-s3` - S3 connection test

## 🛡️ Security Features

- SHA-256 password hashing
- Session-based authentication
- Role-based permissions
- Automatic session expiry
- Secure client ID generation

---

🔐 **Secure** | 📊 **Powerful** | 🎭 **Role-Based** | 🚀 **Ready to Use**