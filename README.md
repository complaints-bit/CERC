# WhatsApp NGO Chatbot (RAG Enabled)

A low-cost WhatsApp chatbot for NGOs using Flask, Meta Cloud API, and RAG (retrieval-augmented generation) with local PDFs.

## 🚀 Setup Steps

### 1. Prerequisites
- Python 3.10+
- WhatsApp Business Account (Meta Developers)
- `ngrok` installed

### 2. Configuration
The `.env` file is already created with your credentials. verify `PHONE_NUMBER_ID`, `ACCESS_TOKEN`, and `VERIFY_TOKEN` match your Meta dashboard.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Prepare Data (RAG)
1. Place your NGO PDF file in this folder and rename it to **`ngo_data.pdf`**.
2. Run the ingestion script to create the search index:
   ```bash
   python ingest.py
   ```
   This will create a `ngo_index` folder.

### 5. Run the Server
```bash
python app.py
```
The server will start on port 5000.

### 6. Expose to Internet
In a separate terminal:
```bash
ngrok http 5000
```
Copy the secure URL (e.g., `https://abcd-123.ngrok-free.app`).

### 7. Configure WhatsApp Webhook
1. Go to [Meta Developers > WhatsApp > Configuration](https://developers.facebook.com/apps/).
2. Click **Edit** near "Callback URL".
3. Enter your ngrok URL + `/webhook` (e.g., `https://abcd-123.ngrok-free.app/webhook`).
4. Enter the Verify Token: `ngo_demo_token`.
5. Click **Verify and Save**.

## 🧪 Testing
Send a message to your WhatsApp test number. 
- If `ngo_data.pdf` WAS ingested: It will reply with relevant snippets from the PDF.
- If NOT ingested: It will echo your message.

## 📂 Project Structure
- `app.py`: Main Flask webhook server
- `ingest.py`: Script to process PDF -> Vector DB
- `requirements.txt`: Dependencies
- `.env`: API Keys
