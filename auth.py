import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import uuid

class AuthManager:
    def __init__(self):
        self.users_file = "users.json"
        self.sessions_file = "sessions.json"
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """Ensure user and session files exist"""
        if not os.path.exists(self.users_file):
            self.save_users({})
        if not os.path.exists(self.sessions_file):
            self.save_sessions({})
    
    def load_users(self) -> Dict:
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_users(self, users: Dict):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def load_sessions(self) -> Dict:
        """Load sessions from JSON file"""
        try:
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_sessions(self, sessions: Dict):
        """Save sessions to JSON file"""
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_client_id(self, username: str, role: str) -> str:
        """Generate client ID based on username and role"""
        timestamp = datetime.now().strftime("%Y%m%d")
        role_prefix = "INV" if role == "investor" else "IVE"  # INV for investor, IVE for investee
        username_hash = hashlib.md5(username.encode()).hexdigest()[:6].upper()
        return f"{role_prefix}_{username_hash}_{timestamp}"
    
    def register_user(self, username: str, password: str, role: str) -> Tuple[bool, str, str]:
        """Register a new user and return success status, message, and session_id"""
        users = self.load_users()
        
        if username in users:
            return False, "Username already exists", ""
        
        if not username or not password:
            return False, "Username and password are required", ""
        
        if role not in ["investor", "investee"]:
            return False, "Invalid role selected", ""
        
        client_id = self.generate_client_id(username, role)
        
        users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "full_name": username.title(),  # Use username as display name
            "client_id": client_id,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat()
        }
        
        self.save_users(users)
        
        # Automatically create session for new user
        session_id = self.create_session(username)
        
        return True, f"User registered successfully! Client ID: {client_id}", session_id
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Authenticate user credentials"""
        users = self.load_users()
        
        if username not in users:
            return False, None
        
        user = users[username]
        if user["password"] == self.hash_password(password):
            # Update last login
            user["last_login"] = datetime.now().isoformat()
            users[username] = user
            self.save_users(users)
            return True, user
        
        return False, None
    
    def create_session(self, username: str) -> str:
        """Create a new session for authenticated user"""
        session_id = str(uuid.uuid4())
        sessions = self.load_sessions()
        
        sessions[session_id] = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        self.save_sessions(sessions)
        return session_id
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Validate session and return username if valid"""
        sessions = self.load_sessions()
        
        if session_id not in sessions:
            return False, None
        
        session = sessions[session_id]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            # Session expired, remove it
            del sessions[session_id]
            self.save_sessions(sessions)
            return False, None
        
        return True, session["username"]
    
    def logout_user(self, session_id: str):
        """Logout user by removing session"""
        sessions = self.load_sessions()
        if session_id in sessions:
            del sessions[session_id]
            self.save_sessions(sessions)
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        users = self.load_users()
        return users.get(username)

def show_login_page():
    """Display login/register page"""
    st.set_page_config(
        page_title="Excel Analysis - Login",
        page_icon="🔐",
        layout="centered"
    )
    
    # Initialize auth manager
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    
    auth = st.session_state.auth_manager
    
    # Header
    st.title("🔐 Excel Analysis Platform")
    st.markdown("**Secure Login for Investors and Investees**")
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.header("Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("👤 Username")
            password = st.text_input("🔒 Password", type="password")
            
            login_button = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
            
            if login_button:
                if username and password:
                    success, user_info = auth.authenticate_user(username, password)
                    if success:
                        # Create session
                        session_id = auth.create_session(username)
                        st.session_state.session_id = session_id
                        st.session_state.current_user = user_info
                        st.session_state.authenticated = True
                        st.success(f"✅ Welcome back, {user_info['full_name']}!")
                        st.success(f"🆔 Your Client ID: **{user_info['client_id']}**")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
            

    
    with tab2:
        st.header("Create New Account")
        
        with st.form("register_form"):
            reg_username = st.text_input("👤 Username", help="Choose a unique username")
            reg_password = st.text_input("🔒 Password", type="password", help="Choose a strong password")
            reg_confirm_password = st.text_input("🔒 Confirm Password", type="password")
            
            reg_role = st.selectbox(
                "🎭 Role", 
                ["investor", "investee"],
                help="Select your role: Investor (provides capital) or Investee (receives investment)"
            )
            
            # Role descriptions
            if reg_role == "investor":
                st.info("🏦 **Investor**: You provide capital and analyze investment opportunities")
            else:
                st.info("🏢 **Investee**: You seek investment and provide business data for analysis")
            
            register_button = st.form_submit_button("📝 Register", type="primary", use_container_width=True)
            
            if register_button:
                if not all([reg_username, reg_password, reg_confirm_password]):
                    st.warning("⚠️ Please fill in all fields")
                elif reg_password != reg_confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(reg_password) < 6:
                    st.error("❌ Password must be at least 6 characters long")
                else:
                    success, message, session_id = auth.register_user(reg_username, reg_password, reg_role)
                    if success:
                        st.success(f"✅ {message}")
                        # Auto-login after successful registration
                        if session_id:
                            # Get user info for session
                            success_auth, user_info = auth.authenticate_user(reg_username, reg_password)
                            if success_auth:
                                st.session_state.session_id = session_id
                                st.session_state.current_user = user_info
                                st.session_state.authenticated = True
                                st.success("🎉 Welcome! You're now logged in!")
                                st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            🔐 Secure Authentication | 📊 Excel Analysis Platform<br>
            🏦 For Investors and 🏢 Investees
        </div>
        """, 
        unsafe_allow_html=True
    )

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        return False
    
    # Validate session if exists
    if 'session_id' in st.session_state and 'auth_manager' in st.session_state:
        auth = st.session_state.auth_manager
        valid, username = auth.validate_session(st.session_state.session_id)
        if not valid:
            # Session expired
            st.session_state.authenticated = False
            if 'current_user' in st.session_state:
                del st.session_state.current_user
            if 'session_id' in st.session_state:
                del st.session_state.session_id
            return False
    
    return True

def logout_user():
    """Logout current user"""
    if 'session_id' in st.session_state and 'auth_manager' in st.session_state:
        auth = st.session_state.auth_manager
        auth.logout_user(st.session_state.session_id)
    
    # Clear session state
    keys_to_remove = ['authenticated', 'current_user', 'session_id', 'last_session_id']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()

def get_current_user():
    """Get current authenticated user info"""
    return st.session_state.get('current_user')

def get_current_client_id():
    """Get current user's client ID"""
    user = get_current_user()
    return user['client_id'] if user else None

