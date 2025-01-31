import subprocess

def main():
	subprocess.run(["streamlit", "run", "src/sqlbot/run_as_app.py"])

if __name__ == "__main__":
	main()