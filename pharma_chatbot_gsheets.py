import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS  # Using local FAISS instead of PGVector
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()


# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")  # From your Google Sheet URL

def connect_to_gsheets():
    """Authenticate and connect to Google Sheets"""
    creds = Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)

def load_pharma_data():
    """Load data from Google Sheets and create documents"""
    sheet = connect_to_gsheets()
    
    # Load medicines
    medicines_df = pd.DataFrame(sheet.worksheet("Medicines").get_all_records())
    medicine_docs = [
        Document(
            page_content=f"Medicine: {row['Name']}\nGeneric: {row['Generic Name']}\nUses: {row['Uses']}\nSide Effects: {row['Side Effects']}\nBrands: {row['Common Brands (India)']}",
            metadata={
                "type": "medicine",
                "prescription": row["Prescription"],
                "brands": row["Common Brands (India)"]
            }
        ) for _, row in medicines_df.iterrows()
    ]
    
    # Load diseases
    diseases_df = pd.DataFrame(sheet.worksheet("Diseases").get_all_records())
    disease_docs = [
        Document(
            page_content=f"Disease: {row['Name']}\nSymptoms: {row['Symptoms']}\nMedicines: {row['Recommended Medicines']}\nPrecautions: {row['Precautions']}",
            metadata={
                "type": "disease",
                "symptoms": row["Symptoms"],
                "medicines": row["Recommended Medicines"]
            }
        ) for _, row in diseases_df.iterrows()
    ]
    
    # Load symptoms
    symptoms_df = pd.DataFrame(sheet.worksheet("Symptoms").get_all_records())
    symptom_docs = [
        Document(
            page_content=f"Symptom: {row['Name']}\nAssociated Diseases: {row['Associated Diseases']}\nSeverity: {row['Severity']}",
            metadata={
                "type": "symptom",
                "diseases": row["Associated Diseases"],
                "severity": row["Severity"]
            }
        ) for _, row in symptoms_df.iterrows()
    ]
    
    return medicine_docs + disease_docs + symptom_docs

def get_vectorstore(docs):
    """Create vector store from documents"""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    return FAISS.from_documents(docs, embeddings)

def create_qa_chain(vectorstore):
    """Create QA chain with Groq"""
    PROMPT_TEMPLATE = """You are an Indian pharmaceutical assistant. Provide:
    1. Medicine info including Indian brands
    2. Disease info with symptoms and treatments
    3. Always recommend doctor consultation for prescriptions
    4. Never suggest prescription medicines without doctor advice
    
    Context: {context}
    Question: {question}
    Answer:"""
    
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )
    
    llm = ChatGroq(
        model="mistral-saba-24b",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

def main():
    st.set_page_config(page_title="Pharma Assistant", page_icon="💊")
    st.title("💊 Pharmaceutical Assistant")
    st.write("Ask about medicines, symptoms, or diseases")
    
    # Load data and initialize
    if "qa_chain" not in st.session_state:
        with st.spinner("Loading pharmaceutical knowledge..."):
            try:
                docs = load_pharma_data()
                st.success(f"Loaded {len(docs)} documents from Google Sheets")
                vectorstore = get_vectorstore(docs)
                st.success("Vector store created successfully")
                st.session_state.qa_chain = create_qa_chain(vectorstore)
                st.success("QA chain initialized")
            except Exception as e:
                st.error(f"Initialization failed: {str(e)}")
                st.error(f"Full error: {repr(e)}")  # Show complete error details
                st.stop()
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I can help with medicine information, symptoms analysis, and disease information. How can I help you today?"}
        ]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.qa_chain({"query": prompt})
                    response = result["result"]
                    
                    # Add sources
                    if "source_documents" in result:
                        sources = list(set([doc.metadata["type"] for doc in result["source_documents"]]))
                        response += f"\n\nSources: {', '.join(sources)}"
                    
                    response += "\n\n⚠️ Disclaimer: Consult a doctor before taking any medication."
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()