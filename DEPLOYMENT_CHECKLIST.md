# i nik Deployment Checklist

## Required Secrets

Set these in Streamlit Cloud / deployment environment:

- GEMINI_API_KEY
- SUPABASE_URL
- SUPABASE_KEY
- N8N_EVENT_WEBHOOK_URL

## Entrypoint

```bash
streamlit run app.py
