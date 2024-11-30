# Hide warnings
import warnings
warnings.filterwarnings("ignore")

import pandas as pd


yt_data=pd.read_csv('data/youtube_playlist_urls_and_thumbnails.csv')


import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
HF_API_KEY=os.getenv("HF_API_KEY")

from langchain_google_genai import ChatGoogleGenerativeAI
llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", google_api_key=GOOGLE_API_KEY,temperature=0)


#Loading Report
from langchain.document_loaders import PyPDFLoader

loader = PyPDFLoader("data/Health Report- Yash Sakhuja.pdf")
pages = loader.load()



#Chunking & Splitting the document
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)

splits= text_splitter.split_documents(pages)

#Embedding the Document using HF-SentenceTransformer Model
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=HF_API_KEY, model_name="sentence-transformers/all-MiniLM-l6-v2"
)


#Storing in VectorDB (FAISS)
from langchain.vectorstores import FAISS
vectordb = FAISS.from_documents(splits, embedding=embeddings)


#vectordb.delete_collection()

import pandas as pd
data=pd.read_csv("data/youtube_playlist_urls_and_thumbnails.csv")

ex_names_list = ",".join(data['Exercise_Name'].astype(str).tolist())



exercise_names_list = ex_names_list.split(",")  # Splitting on double spaces

# Specify the directory and filename
directory = "data"
filename = "exercise_names.txt"
file_path = os.path.join(directory, filename)

# Create the directory if it doesn't exist
os.makedirs(directory, exist_ok=True)

# Open the file in write mode within the specified directory
with open(file_path, 'w') as file:
    # Write each exercise name on a new line
    for exercise in exercise_names_list:
        # Remove any leading/trailing whitespace and write to file
        file.write(f"{exercise.strip()}\n")

print(f"Data has been written to {file_path}.")

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# Define your desired data structure.
class Parsing(BaseModel):
    day_of_week: str = Field(description="Give me day of the week the exercise is for.")
    exercise_name: str = Field(description="Give me the exercise name from the list.")
    sets_reps: str = Field(description="Give me the sets and reps I have to do that exercise for.")
    rest: str = Field(description="Give me the rest I have to take between consecutive reps.")

parser = JsonOutputParser(pydantic_object=Parsing)

from langchain.prompts import PromptTemplate


template= """ Assume the role of my gym trainer who would go through my health checkup report and help me design a training plan
to help me improve my physical health and keep me free from cardiac problems all my life.

I am 23 year old male who would like to hit the gym for 1 hour a day and my purpose is to maintain a good heart condition and
reduce belly fat and build muscle mass without any protien intake from outside sources other than healthy balance diet.

Use My latest health reports for context and understanding my vitals and body condition.
{context}

Only give exercise names from the list of exercises mentioned below. Do not give any other exercise name. Make Sure you give the names with same exact spellings as mentioned in list.
\n{ex_names}\n

Make sure you maintain this regime
Monday: Cardio & Legs
Wednesday: Chest & Triceps
Thursday: Core
Friday: Back & Biceps
Saturday: Shoulders & Core


I start all my Gym sessions with a cycling of 30 minutes. Don't metnion cycling in the list you provide just give me the list of exercises after cycling.

So all exercises or weight training should begin after that and I do not want to spend only 30 minutes (exclusding cycling time).DS_Store
Do not give more than 5 exercises in a day.

\n{format_instructions}\n

Question: {question}
Helpful Answer:  """



QA_CHAIN_PROMPT = PromptTemplate.from_template(template,partial_variables={"format_instructions": parser.get_format_instructions()})


chain =  QA_CHAIN_PROMPT | llm_model | parser

question="Suggest me a list of exercises in a day if visit the Gym 5 days a week with 2 rest days on Tuesday and Sunday."

response= chain.invoke({"context":vectordb.as_retriever(),"ex_names":ex_names_list,"question": question})

df = pd.DataFrame(response)

result = pd.merge(df, data, left_on='exercise_name',right_on="Exercise_Name", how='inner')
result = result.drop(columns=['Exercise_Name'])
result = result.rename(columns={'exercise_name': 'exercise_name_list'})

## What's the day today
import datetime

# Get today's date
today = datetime.date.today()

# Get the day of the week (0 = Monday, 6 = Sunday)
day_of_week_today = today.strftime("%A")

if day_of_week_today not in ["Tuesday", "Sunday"]:
    filtered_result=result[result["day_of_week"]==day_of_week_today]
    filtered_result=filtered_result.reset_index(drop=True)

    output_template= """
    For the following text, extract only the name of the exercise and nothing else.

    Return as simple string and no escape sequences or markdown.

    Return Null if not appropriate answer available. Do not hallucinate.

    text: {text}

    {format_instructions}

    """

    from langchain.prompts import ChatPromptTemplate
    from langchain.output_parsers import StructuredOutputParser
    from langchain.output_parsers import ResponseSchema
    import time


    exercise_name_schema = ResponseSchema(name="Exercise_Name",
                                description="What is the name of the exercise?")

    response_schemas = [exercise_name_schema]

    output_parser= StructuredOutputParser.from_response_schemas(response_schemas)

    format_instructions = output_parser.get_format_instructions()



    filtered_result["Exercise_Name"]=None

    for i in range(len(filtered_result)):

        prompt= ChatPromptTemplate.from_template(template=output_template)

        ## Making a prompt by looping over each item_description one by one
        messages= prompt.format_messages(text=filtered_result['exercise_name_list'].iloc[i],
                                        format_instructions=format_instructions)

        time.sleep(5)
        response= llm_model(messages)

        ## Getting the response and Parsing it to a json dictionary
        parsed_response= output_parser.parse(response.content)


        ## Now store this dictionary output back to the Answer field
        filtered_result['Exercise_Name'].iloc[i]= parsed_response

        messages=""

    filtered_result["Display_Name"] = None
    for i in range(len(filtered_result)):
        output=filtered_result['Exercise_Name'].iloc[i]

        filtered_result['Display_Name'].iloc[i]= output.get('Exercise_Name')


        import datetime

        markdown_output = ""

        # Get the day of the week today
        day_of_week_today = datetime.datetime.now().strftime("%A")
        markdown_output += "Exercises for " + str(day_of_week_today) + " : " + str(datetime.date.today()) + "\n\n"

    # Iterate through the DataFrame and build markdown output
    for idx, row in filtered_result.iterrows():
        display_name = row['Display_Name']
        sets_reps = row['sets_reps']
        rest = row['rest']
        thumbnail_url = row['Thumbnail_URL']
        url = row['URL']

        markdown_output += f"*{idx + 1}) {display_name}*\n"
        markdown_output += f"{sets_reps}\n"
        markdown_output += f"Rest: {rest}\n"
        markdown_output += f"[PureGym Video Link] ({url})\n\n"

    print(markdown_output)


    import os
    from dotenv import load_dotenv

    load_dotenv()

    from twilio.rest import Client

    account_sid=os.getenv("TWILIO_ACCOUNT_SID")
    auth_token=os.getenv("TWILIO_AUTH_TOKEN")

    client = Client(account_sid, auth_token)

    # Sending a message
    from_whatsapp_number = 'whatsapp:+14155238886'  # Twilio sandbox number
    to_whatsapp_number = 'whatsapp:+44XXXXXXXXXX' #Change to your whatsapp number

    message = client.messages.create(
        body=markdown_output,
        from_=from_whatsapp_number,
        to=to_whatsapp_number
    )

    print("Message sent! SID:", message.sid)

else:
    print("It's a Rest Day mate!")
