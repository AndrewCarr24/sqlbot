import subprocess
import os

def main():
    # Get the current directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to run_as_app.py
    run_as_app_path = os.path.join(current_dir, "run_as_app.py")
    
    try:
        # Run the Streamlit app
        subprocess.run(["streamlit", "run", run_as_app_path])
    except KeyboardInterrupt:
        print("Stopping the app...")

if __name__ == "__main__":
    main()