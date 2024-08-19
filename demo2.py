import os
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Set API key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Initialize embeddings model
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Load and process documents
loader = CSVLoader(file_path="C:/Users/khair/Downloads/en-FAQ.csv")  # Update with your file path
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
docs = text_splitter.split_documents(documents=documents)

# Create and save vector store
vectorstore = FAISS.from_documents(docs, embeddings_model)
vectorstore.save_local("faiss_index_react")

# Setup retrieval QA
retriever = vectorstore.as_retriever()

prompt_template = """
    You are a knowledgeable assistant. Answer the following question using the provided context:

    **Question**: {question}

    **Context**:
    {context}

    **Answer**:
    """

prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

qa = RetrievalQA.from_chain_type(
    llm=GoogleGenerativeAI(model="models/text-bison-001", temperature=0),
    chain_type_kwargs={"prompt": prompt},
    retriever=retriever
)

def listen_for_command():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio)
            print(f"Command recognized: {command}")
            return command.lower().strip()
    except sr.UnknownValueError:
        print("Sorry, I did not understand the audio.")
        return None
    except sr.RequestError:
        print("Sorry, there was an issue with the request.")
        return None

def respond(response):
    engine.say(response)
    engine.runAndWait()

def open_powerpoint():
    respond("Opening PowerPoint.")
    os.system("start powerpnt")  # This will start PowerPoint

def process_command(command):
    if command in ["open slides", "open slide", "open powerpoint", "open presentation"]:
        open_powerpoint()
    else:
        # Handle as a query for the Q&A system
        response = qa.invoke(command)
        respond(response["result"])

def main():
    while True:
        command = listen_for_command()
        if command:
            process_command(command)
        else:
            respond("Sorry, I didn't understand that.")
        
        # Break the loop if the user says 'exit'
        if command and ["exit","quit","stop"] in command:
            respond("Goodbye!")
            break

if __name__ == "__main__":
    main()