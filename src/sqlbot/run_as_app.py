import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool
from sqlalchemy import create_engine 
import os 
import time 
import sqlbot
import importlib.resources as pkg_resources
from sqlbot import data
from dotenv import load_dotenv, set_key
load_dotenv()

# Configure the Streamlit app
st.set_page_config(page_title="Chinook Chatbot", page_icon=":speech_balloon:", layout="wide")

def get_api_key():
	dotenv_path = os.path.join(os.getcwd(), ".env")
	load_dotenv(dotenv_path)
	api_key = os.getenv("OPENAI_API_KEY")

	if not api_key:
		if not os.path.exists(dotenv_path):
			open(dotenv_path, "w").close()

		if "api_key_submitted" not in st.session_state:
			st.session_state.api_key_submitted = False

		if not st.session_state.api_key_submitted:
			api_key = st.text_input("Please enter your API key:", type="password")

			if st.button("Submit"):
				if api_key:
					os.environ["OPENAI_API_KEY"] = api_key
					set_key(dotenv_path, "OPENAI_API_KEY", api_key)
					st.session_state.api_key = api_key
					st.session_state.api_key_submitted = True
					st.rerun()
				else:
					st.error("No API key provided. Please enter your API key.")
	else:
		st.session_state.api_key = api_key

# Call the function to ensure the API key is set
if "api_key" not in st.session_state:
	get_api_key()

if "api_key" in st.session_state:

	# Initialize session state for chatbot setup
	if "db_metadata" not in st.session_state:
		# Set up the LLM instance
		llm = ChatOpenAI(
			model="gpt-4o-mini",
			temperature=0,
			max_tokens=None,
			timeout=None,
			max_retries=0
		)

		# Connect to the Chinook SQL database
		with pkg_resources.path(data, 'chinook.db') as db_path:
			engine = create_engine(f"sqlite:///{db_path}")
			db_engine = SQLDatabase(engine)

		# Store the main chatbot with system message
		st.session_state.db_metadata = """
			### Tables and Columns

			1. **albums**
			   - AlbumId: INTEGER
			   - Title: NVARCHAR(160)
			   - ArtistId: INTEGER

			2. **artists**
			   - ArtistId: INTEGER
			   - Name: NVARCHAR(120)

			3. **customers**
			   - CustomerId: INTEGER
			   - FirstName: NVARCHAR(40)
			   - LastName: NVARCHAR(20)
			   - Company: NVARCHAR(80)
			   - Address: NVARCHAR(70)
			   - City: NVARCHAR(40)
			   - State: NVARCHAR(40)
			   - Country: NVARCHAR(40)
			   - PostalCode: NVARCHAR(10)
			   - Phone: NVARCHAR(24)
			   - Fax: NVARCHAR(24)
			   - Email: NVARCHAR(60)
			   - SupportRepId: INTEGER

			4. **employees**
			   - EmployeeId: INTEGER
			   - LastName: NVARCHAR(20)
			   - FirstName: NVARCHAR(20)
			   - Title: NVARCHAR(30)
			   - ReportsTo: INTEGER
			   - BirthDate: DATETIME
			   - HireDate: DATETIME
			   - Address: NVARCHAR(70)
			   - City: NVARCHAR(40)
			   - State: NVARCHAR(40)
			   - Country: NVARCHAR(40)
			   - PostalCode: NVARCHAR(10)
			   - Phone: NVARCHAR(24)
			   - Fax: NVARCHAR(24)
			   - Email: NVARCHAR(60)

			5. **genres**
			   - GenreId: INTEGER
			   - Name: NVARCHAR(120)

			6. **invoices**
			   - InvoiceId: INTEGER
			   - CustomerId: INTEGER
			   - InvoiceDate: DATETIME
			   - BillingAddress: NVARCHAR(70)
			   - BillingCity: NVARCHAR(40)
			   - BillingState: NVARCHAR(40)
			   - BillingCountry: NVARCHAR(40)
			   - BillingPostalCode: NVARCHAR(10)
			   - Total: NUMERIC(10,2)

			7. **invoice_items**
			   - InvoiceLineId: INTEGER
			   - InvoiceId: INTEGER
			   - TrackId: INTEGER
			   - UnitPrice: NUMERIC(10,2)
			   - Quantity: INTEGER

			8. **media_types**
			   - MediaTypeId: INTEGER
			   - Name: NVARCHAR(120)

			9. **playlists**
			   - PlaylistId: INTEGER
			   - Name: NVARCHAR(120)

			10. **playlist_track**
				- PlaylistId: INTEGER
				- TrackId: INTEGER

			11. **tracks**
				- TrackId: INTEGER
				- Name: NVARCHAR(200)
				- AlbumId: INTEGER
				- MediaTypeId: INTEGER
				- GenreId: INTEGER
				- Composer: NVARCHAR(220)
				- Milliseconds: INTEGER
				- Bytes: INTEGER
				- UnitPrice: NUMERIC(10,2)
		"""

		st.session_state.chat_model = sqlbot.chatbot.LLMWithHistory(
			llm, 
			tools=[QuerySQLDatabaseTool(db=db_engine)], 
			system_message=f"""
			You are an AI assistant hooked up to a database. Answer any questions about the database.
			{st.session_state.db_metadata} 
			If the user asks a question that requires running a SQL query, include the original query in your final response.
			"""
		)

	st.markdown("""
		<style>
			/* Adjust space between columns */
			.st-emotion-cache-ocqkz7 {
				gap: 2.5rem !important;  /* Moderate gap that won't force wrapping */
			}

			/* Add fixed-length divider */
			.stHorizontalBlock.st-emotion-cache-ocqkz7.eiemyj0::after {
				content: '';
				position: absolute;
				left: 60%;
				top: 0;
				height: 80vh;  /* Fixed height - adjust this value */
				width: 2px;
				background-color: #e6e6e6;
			}

			/* Prevent column wrapping */
			.st-emotion-cache-ocqkz7 {
				flex-wrap: nowrap !important;  /* Prevents columns from wrapping */
				min-width: fit-content;
			}

			/* Reduce space between sidebar and main content */
			[data-testid="stSidebar"][aria-expanded="true"] {
				margin-right: -3rem;  /* Negative margin reduces the gap */
			}

			h1 {
			    font-family: 'Montserrat', sans-serif !important;
			    color: #2C3E50 !important;
			}

			h2 {
			    font-family: 'Arial', monospace !important;
			    color: #2C3E50 !important;
			}
		</style>
	""", unsafe_allow_html=True)

	st.title("SQL Database Chatbot")

	# Create a two-column layout
	left_col, right_col = st.columns([3, 2])

	# Chat container in the left column
	with left_col:
		chat_container = st.container()

		# Chat input and output
		user_text = st.chat_input("Say something")

		if user_text:
			st.session_state.chat_model.send_message_to_llm(user_text, print_response=False)
			response = st.session_state.chat_model.history[-1].content

			# Display the chatbot response
			with st.expander("Chatbot Output", expanded=True):
				response_placeholder = st.empty()
				streamed_response = ""
				for token in response:
					streamed_response += token
					response_placeholder.text(streamed_response)
					time.sleep(0.003)


	# SQL Query pane in the right column with styling
	with right_col:

		# Create a container for the SQL query
		sql_container = st.container()

		# Create the SQL query box
		with sql_container:
			st.header("SQL Query")
			if user_text:
				try:
					st.session_state.chat_model.get_sql_query()
					sql_query = st.session_state.chat_model.query_output
					st.code(sql_query, language="sql")
				except IndexError:
					st.info("No SQL query in this response")

	# Sidebar information
	with st.sidebar:
		st.header("About the Chatbot")
		st.write("""
		This chatbot is connected to the Chinook SQL database. You can use it to query the database and get information about the various tables and columns.
		The Chinook database contains information about albums, artists, customers, and more. Simply type your query in the chat input box, and the chatbot will provide the relevant information.
		""")
		if st.button("Exit"):
			st.stop()