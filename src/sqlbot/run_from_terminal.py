from . import chatbot 
import time 
from dotenv import load_dotenv, set_key
from langchain_openai import ChatOpenAI
import argparse
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool
from sqlalchemy import create_engine 
import getpass
import os 

def start_bot():

    def get_api_key():

        # Define the path for the .env file in the project root directory
        dotenv_path = os.path.join(os.getcwd(), ".env")

        # Load the .env file if it exists
        load_dotenv(dotenv_path)

        # First, check if the API key is in the environment variables
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            return api_key

        # If not, check if the .env file exists, if not, create it
        if not os.path.exists(dotenv_path):
            with open(dotenv_path, "w"):  # Create an empty .env file
                pass
            print(f".env file created at {dotenv_path}")

        # If not, prompt the user to input it securely
        print("API key not found in environment variables or configuration.")
        api_key = getpass.getpass("Please enter your API key: ")

        # Optionally, confirm the key
        if not api_key:
            raise ValueError("No API key provided. Exiting.")

        # Set the API key to the environment variable for future use
        os.environ["OPENAI_API_KEY"] = api_key

        # Save the API key to the .env file if it's not already there
        set_key(dotenv_path, "OPENAI_API_KEY", api_key)
        print(f"API key has been saved to {dotenv_path}.")

        return api_key

    def get_db_path():
        """
        Get the database path from command-line arguments.
        Returns:
            str: The database path.
        """
        # Command line tool with arguments
        parser = argparse.ArgumentParser(description="Run LLM agent with SQL db query tool from the terminal.")
        parser.add_argument("--db", help="Path of local db", required=True)
        args = parser.parse_args()
        print(f"\nConnecting to {args.db}.db . . .")
        return f"{args.db}.db"
    
    # Set API key
    get_api_key()       

    # Get tools for chatbot
    db_path = get_db_path() # f"{sys.argv[1]}.db"
    engine = create_engine(f"sqlite:///{db_path}")
    db_engine = SQLDatabase(engine)


    # Get OpenAI API key
    load_dotenv()

    # Instantiate chatmodel
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=0
    )

    print("""
    Connecting to database and collecting metadata . . .
    """)

    # Query for db metadata 
    initial_query = """
    Query the database to get schema information about the database.
    Return all of the schema information needed to run subsequent queries on the database, including table names and columns names and types for each table.
    """

    # Create temp chatbot for initial query
    chatbot_init = chatbot.LLMWithHistory(llm, 
                                          tools=[QuerySQLDatabaseTool(db = db_engine)], 
                                          system_message="You are an AI assistant connected to a SQL database.")
    chatbot_init.send_message_to_llm(initial_query, print_response=False)

    # Get db metadata from chatbot response
    db_metadata = chatbot_init.history[-1].content

    # Add db metadata to system prompt 
    inp_sys_msg = f"""
    You are an AI assistant hooked up to a database. Answer any questions about the database. 

    Here is the database metadata:

    {db_metadata}

    If the user asks a question that requires running a SQL query, include the original query in your final response.
    """
    # Create main chatbot with system prompt using db metadata 
    chatbot_main = chatbot.LLMWithHistory(llm, 
                                          tools=[QuerySQLDatabaseTool(db = db_engine)], 
                                          system_message=inp_sys_msg)

    print("""
    ##############################
    #                            #
    #     WELCOME TO SQLBOT!!    #
    #                            #
    ##############################
    """)

    exit_commands = ("/exit", "/e")
    should_exit = False

    while not should_exit:
        user_text = ''
        while not len(user_text.strip()): 
            print(">> ", end="", flush=True)
            user_text = input()

            if user_text in exit_commands:
                should_exit = True
                break
            elif len(user_text.strip()) == 0:
                pass
            else:
                print("\n")
                chatbot_main.send_message_to_llm(user_text, print_response=True)
                time.sleep(0.02)

if __name__ == "__main__":
    get_api_key()
    start_bot()
