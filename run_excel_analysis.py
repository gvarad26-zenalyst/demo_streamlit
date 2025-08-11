#!/usr/bin/env python3
"""
Launch script for Excel Analysis Dashboard
"""
import subprocess
import sys

def main():
    """Launch the Excel Analysis Streamlit application"""
    try:
        # Check if streamlit is installed
        subprocess.run([sys.executable, "-c", "import streamlit"], check=True, capture_output=True)
        
        # Launch the Streamlit app
        print("📊 Starting Excel Analysis Dashboard...")
        print("🔗 API Base URL: http://13.60.4.11:8006")
        print("📱 The app will open in your default browser")
        print("=" * 50)
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main_app.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
        
    except subprocess.CalledProcessError:
        print("❌ Error: Streamlit is not installed.")
        print("📦 Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
