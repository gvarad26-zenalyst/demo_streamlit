#!/usr/bin/env python3
"""
Main Excel Analysis Application with Authentication
"""
import streamlit as st
from auth import check_authentication, show_login_page
from excel_analysis_ui import main as excel_main

def main():
    """Main application entry point"""
    # Check if user is authenticated
    if not check_authentication():
        # Show login page if not authenticated
        show_login_page()
    else:
        # Show main Excel analysis dashboard if authenticated
        excel_main()

if __name__ == "__main__":
    main()

