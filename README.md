# 💊 Pharma Assistant Chatbot

An intelligent Streamlit-based chatbot for Indian pharmaceutical queries that integrates data from Google Sheets and leverages LangChain + Groq's LLM for real-time question answering using RAG (Retrieval-Augmented Generation).

---
![image](https://github.com/user-attachments/assets/5a5b085e-f736-4c1a-b32e-f12b0f6c9bff)

---
## 🧠 Features

- **Natural Language Q&A**: Ask about medicines, symptoms, and diseases.
- **Google Sheets Integration**: Centralized, easily editable database for medical info.
- **RAG Architecture**: Combines vector similarity search (FAISS) with LLM responses.
- **Indian Market Focus**: Supports Indian brand names, prescription practices.
- **Streamlit UI**: Conversational interface for seamless interactions.
- **Secure**: Environment variables and service account keys for secure API access.

---

## 🏗️ Architecture Overview
```
User (Streamlit Chat)
↓
LangChain QA Chain
↓
Groq LLM (e.g., Mistral-SABA-24B)
↓
FAISS VectorStore ← Embedded Medical Docs
↑
Google Sheets (Medicines, Diseases, Symptoms)
```
---

## 🗂️ Folder Structure
```
.
├── pharma\_chatbot\_gsheets.py     # Main application script
├── credentials.json              # Google service account key (NOT to be committed)
└── README.md                     # This file
```
---

## ⚙️ Setup Instructions

### 1. 🔑 Environment Setup

Create a `.env` file with the below template

```env
SPREADSHEET_ID=your_google_sheet_id
GROQ_API_KEY=your_groq_api_key
````

### 2. 📋 Google Sheets Preparation

Your spreadsheet should have **three worksheets**:

* `Medicines`: Columns - `Name`, `Generic Name`, `Uses`, `Side Effects`, `Common Brands (India)`, `Prescription`
* `Diseases`: Columns - `Name`, `Symptoms`, `Recommended Medicines`, `Precautions`
* `Symptoms`: Columns - `Name`, `Associated Diseases`, `Severity`

### 3. 🔐 Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a service account with Sheets API access.
3. Download the `credentials.json` file and place it in the root directory.
4. Share your Google Sheet with the service account email.

### 4. 🧪 Install Requirements

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the App

```bash
streamlit run pharma_chatbot_gsheets.py
```

---

## 📦 Core Modules

| Module               | Description                                                     |
| -------------------- | --------------------------------------------------------------- |
| `connect_to_gsheets` | Authenticates and reads Google Sheets                           |
| `load_pharma_data`   | Parses and converts rows into LangChain `Document` objects      |
| `get_vectorstore`    | Creates a FAISS-based vector store using HuggingFace embeddings |
| `create_qa_chain`    | Builds a QA chain using Groq’s Mistral model                    |
| `main`               | Streamlit UI logic for chatbot functionality                    |

---

## 🛡️ Disclaimer

This tool is intended for **informational purposes only** and **does not replace professional medical advice**. Always consult a licensed physician before taking any medication.

```
