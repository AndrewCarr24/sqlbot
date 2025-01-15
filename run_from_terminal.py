import chatbot 
import time 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

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
                                      tools=chatbot.get_tools(), 
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
                                      tools=chatbot.get_tools(), 
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


