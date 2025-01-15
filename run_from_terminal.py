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
bedrock_llm_with_history = chatbot.LLMWithHistory(llm,
                                          tools = chatbot.get_tools()[:1],
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


