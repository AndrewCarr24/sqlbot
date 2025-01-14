import chatbot 
import time 
# from langchain_ollama import ChatOllama
# from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
load_dotenv()
# Initialize the chatbot
mistral_llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=24,
)

# ollama_3_2_llm = ChatOllama(
#     model="llama3.2",
#     temperature=0,
#     # other params...
# )
# llm = HuggingFaceEndpoint(
#     repo_id="HuggingFaceH4/zephyr-7b-beta",
#     task="text-generation",
#     max_new_tokens=512,
#     do_sample=False,
#     repetition_penalty=1.03,
# )
# chat_model = ChatHuggingFace(llm=llm).bind_tools(chatbot.get_tools())


inp_sys_msg = """
You are an AI assistant hooked up to the Chinook. 

Answer any questions about the Chinook database. 

Here is the schema of the Chinook database:

### Tables and Columns

#### albums
- **AlbumId**: INTEGER (Primary Key)
- **Title**: NVARCHAR(160)
- **ArtistId**: INTEGER

#### artists
- **ArtistId**: INTEGER (Primary Key)
- **Name**: NVARCHAR(120)

#### customers
- **CustomerId**: INTEGER (Primary Key)
- **FirstName**: NVARCHAR(40)
- **LastName**: NVARCHAR(20)
- **Company**: NVARCHAR(80)
- **Address**: NVARCHAR(70)
- **City**: NVARCHAR(40)
- **State**: NVARCHAR(40)
- **Country**: NVARCHAR(40)
- **PostalCode**: NVARCHAR(10)
- **Phone**: NVARCHAR(24)
- **Fax**: NVARCHAR(24)
- **Email**: NVARCHAR(60)
- **SupportRepId**: INTEGER

#### employees
- **EmployeeId**: INTEGER (Primary Key)
- **LastName**: NVARCHAR(20)
- **FirstName**: NVARCHAR(20)
- **Title**: NVARCHAR(30)
- **ReportsTo**: INTEGER
- **BirthDate**: DATETIME
- **HireDate**: DATETIME
- **Address**: NVARCHAR(70)
- **City**: NVARCHAR(40)
- **State**: NVARCHAR(40)
- **Country**: NVARCHAR(40)
- **PostalCode**: NVARCHAR(10)
- **Phone**: NVARCHAR(24)
- **Fax**: NVARCHAR(24)
- **Email**: NVARCHAR(60)

#### genres
- **GenreId**: INTEGER (Primary Key)
- **Name**: NVARCHAR(120)

#### invoices
- **InvoiceId**: INTEGER (Primary Key)
- **CustomerId**: INTEGER
- **InvoiceDate**: DATETIME
- **BillingAddress**: NVARCHAR(70)
- **BillingCity**: NVARCHAR(40)
- **BillingState**: NVARCHAR(40)
- **BillingCountry**: NVARCHAR(40)
- **BillingPostalCode**: NVARCHAR(10)
- **Total**: NUMERIC(10,2)

#### invoice_items
- **InvoiceLineId**: INTEGER (Primary Key)
- **InvoiceId**: INTEGER
- **TrackId**: INTEGER
- **UnitPrice**: NUMERIC(10,2)
- **Quantity**: INTEGER

#### media_types
- **MediaTypeId**: INTEGER (Primary Key)
- **Name**: NVARCHAR(120)

#### playlists
- **PlaylistId**: INTEGER (Primary Key)
- **Name**: NVARCHAR(120)

#### playlist_track
- **PlaylistId**: INTEGER (Primary Key)
- **TrackId**: INTEGER

#### tracks
- **TrackId**: INTEGER (Primary Key)
- **Name**: NVARCHAR(200)
- **AlbumId**: INTEGER
- **MediaTypeId**: INTEGER
- **GenreId**: INTEGER
- **Composer**: NVARCHAR(220)
- **Milliseconds**: INTEGER
- **Bytes**: INTEGER
- **UnitPrice**: NUMERIC(10,2)

### Common Values of Categorical Columns

#### genres (Name)
- Rock
- Jazz
- Metal
- Alternative & Punk
- Rock And Roll
- Blues
- Latin
- Reggae
- Pop
- Soundtrack
- Bossa Nova
- Easy Listening
- Heavy Metal
- R&B/Soul
- Electronica/Dance
- World
- Hip Hop/Rap
- Science Fiction
- TV Shows
- Sci Fi & Fantasy
- Drama
- Comedy
- Alternative
- Classical
- Opera

#### media_types (Name)
- MPEG audio file
- Protected AAC audio file
- Protected MPEG-4 video file
- Purchased AAC audio file
- AAC audio file

Always include the SQL query in your response.
"""

# Create chatbot object with history, tools, and system prompt 
bedrock_llm_with_history = chatbot.LLMWithHistory(mistral_llm,
                                          tools = chatbot.get_tools(),
                                          system_message = inp_sys_msg)


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
            bedrock_llm_with_history.send_message_to_llm(user_text)
            time.sleep(0.02)


