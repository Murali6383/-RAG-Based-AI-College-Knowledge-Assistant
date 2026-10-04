# TruthGuard AI — College/Company Knowledge Assistant

A grounded RAG chatbot designed for college/company documents:
- College regulations
- Attendance rules
- Exam regulations
- Placement guidelines
- Hostel rules
- Leave policy
- Department handbook

## Core idea
The LLM is NOT treated as the source of truth. The system retrieves evidence from your uploaded documents, applies deterministic rules when applicable, and only then asks Gemini to explain the result.

## Hallucination protection
1. Retrieve relevant chunks from your documents.
2. Reject low-relevance questions.
3. For attendance-style numeric policy questions, use a rule engine instead of letting the LLM calculate eligibility.
4. Gemini receives only retrieved context and strict grounding instructions.
5. Response includes source names and retrieval score.
6. If evidence is missing, the assistant says it does not know instead of inventing an answer.

## Windows setup
### Backend
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Add your Gemini API key to `.env`.

Put your PDF files into:
`backend/data/documents/`

Start:
```powershell
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```
Open the URL shown by Vite, normally http://localhost:5173.

## Build the document index
After adding/changing PDFs:
```powershell
curl -X POST http://127.0.0.1:8000/admin/reindex
```
Or use the frontend's Reindex button.

## Example
Question:
`I have 70% attendance. Can I attend the exam?`

If your attendance document says 75% minimum, the backend extracts 70 and 75 and the deterministic rule engine returns NOT ELIGIBLE. Gemini is used only to phrase the evidence-based response.

## Important
This project does not guarantee zero hallucinations. It implements practical grounding, abstention, source attribution, and deterministic policy checks to reduce unsupported answers.
