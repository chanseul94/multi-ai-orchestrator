# Multi-AI Orchestrator

Gemini produces an independent analysis. OpenAI reviews that analysis and writes the final answer.

## Required secrets

Configure these as hosting secrets, never as repository files:

- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `APP_PASSWORD`
- `CAREER_PROFILE` (multiline master career profile; automatically included in every request)
Optional variables:

- `GEMINI_MODEL` (default: `gemini-3.1-flash-lite`)
- `OPENAI_MODEL` (default: `gpt-6.1-sol`)

Deploy from a private GitHub repository to Streamlit Community Cloud. Add both API keys through Streamlit's **Advanced settings → Secrets** field; never commit them.
