
import io
import requests
import streamlit as st
from pypdf import PdfReader

# ---------------- APP CONFIG ----------------
st.set_page_config(
    page_title="StudyNova | AI Study Assistant",
    page_icon="📚",
    layout="wide",
)

MODEL = "@cf/meta/llama-3.1-8b-instruct-fast"
API_BASE = "https://api.cloudflare.com/client/v4/accounts"

# ---------------- AI CONNECTION ----------------
def ask_ai(prompt):
    try:
        try:
            account_id = str(st.secrets.get("CLOUDFLARE_ACCOUNT_ID", "")).strip()
            api_token = str(st.secrets.get("CLOUDFLARE_API_TOKEN", "")).strip()
        except Exception:
            return (
                "SETUP REQUIRED: StudyNova cannot read its Cloudflare secrets. "
                "Open your app in Streamlit Cloud, go to Settings > Secrets, "
                "and check that CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN "
                "are saved there. Never paste the token into chat or public GitHub."
            )

        if not account_id or not api_token:
            return (
                "SETUP REQUIRED: Cloudflare credentials are missing or blank. "
                "Open Streamlit Cloud > Settings > Secrets and check that "
                "CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN are present."
            )

        url = f"{API_BASE}/{account_id}/ai/run/{MODEL}"

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
            json={
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are StudyNova, a helpful AI study assistant. "
                            "Explain concepts clearly in simple English. "
                            "Use headings, examples, and bullet points when useful. "
                            "Base answers on the student's provided notes when "
                            "available. If information is missing, say so."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 700,
                "temperature": 0.4,
            },
            timeout=90,
        )

        if not response.ok:
            # Cloudflare returns structured error codes. Use them to give
            # students safe, useful guidance without exposing request secrets.
            try:
                error_payload = response.json()
            except ValueError:
                error_payload = {}

            cloudflare_errors = error_payload.get("errors", [])
            error_messages = " ".join(
                str(item.get("message", ""))
                for item in cloudflare_errors
                if isinstance(item, dict)
            ).lower()
            error_codes = {
                str(item.get("code", ""))
                for item in cloudflare_errors
                if isinstance(item, dict)
            }

            if response.status_code in (401, 403):
                return (
                    "Cloudflare authentication failed. Check the API token, "
                    "its permissions, and the account ID in Streamlit Secrets."
                )
            if response.status_code == 404:
                return (
                    "The AI model or endpoint was not found. "
                    "Check the current model ID in Cloudflare's model catalogue."
                )
            if response.status_code == 429:
                if "3036" in error_codes or "daily free allocation" in error_messages:
                    return (
                        "StudyNova has used today's free Cloudflare AI allowance. "
                        "It resets at 00:00 UTC (5:30 AM India time). No payment "
                        "is needed for this message—please try again after the reset."
                    )
                return (
                    "The AI service is temporarily rate-limited or busy. "
                    "Wait a little and try again."
                )
            if response.status_code in (500, 502, 503, 504):
                return (
                    "The AI service is temporarily unavailable. Your notes are "
                    "still on this page; please wait a little and try again."
                )

            return (
                f"Cloudflare returned HTTP {response.status_code}. "
                "Please check the AI settings or try again later."
            )

        data = response.json()
        result = data.get("result", {})

        # Support both chat-style and text-style responses.
        if result.get("response"):
            return result["response"]

        choices = result.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get(
                "content", "The AI returned an empty response."
            )

        return "The AI returned an unexpected response. Please try again."

    except requests.Timeout:
        return "The AI request timed out. Please try again."
    except requests.RequestException:
        return "Could not connect to the AI service. Check your internet connection."
    except Exception as exc:
        # Do not display secrets or raw request headers.
        st.error(f"Unexpected error: {type(exc).__name__}")
        return "Something went wrong. Please check your app settings."


# ---------------- APP HEADER ----------------
st.title("📚 StudyNova")
st.subheader("Your AI-powered study companion")
st.write(
    "Understand your notes, summarise chapters, create quizzes, "
    "and ask questions in one place."
)

with st.sidebar:
    st.header("🎓 StudyNova")
    st.caption("Learn smarter, one concept at a time.")
    st.markdown("**Available tools**")
    st.write("📄 Read PDF notes")
    st.write("📝 Summarise study material")
    st.write("💡 Explain difficult concepts")
    st.write("❓ Generate practice quizzes")
    st.write("🤖 Ask study questions")
    st.divider()
    st.caption("AI responses require correctly configured Cloudflare credentials and available service quota.")

# ---------------- NOTES INPUT ----------------
st.header("1. Add your study material")

uploaded_file = st.file_uploader(
    "Upload a text-based PDF (optional)",
    type=["pdf"],
)

pdf_text = ""

if uploaded_file is not None:
    if st.button("📖 Read PDF"):
        try:
            reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
            pdf_text = "\n".join(
                page.extract_text() or "" for page in reader.pages
            )
            if pdf_text.strip():
                st.session_state["study_notes"] = pdf_text
                st.success(
                    f"Extracted text from {len(reader.pages)} PDF pages."
                )
            else:
                st.warning(
                    "No selectable text was found. This PDF may contain scanned images."
                )
        except Exception:
            st.error("Could not read this PDF. Please check the file and try again.")

notes = st.text_area(
    "Paste your notes or chapter text here",
    value=st.session_state.get("study_notes", ""),
    height=220,
    placeholder="Paste your class notes, definitions, or chapter content...",
)

if notes != st.session_state.get("study_notes", ""):
    st.session_state["study_notes"] = notes

# ---------------- STUDY TOOLS ----------------
st.header("2. Choose a study tool")

col1, col2, col3 = st.columns(3)

with col1:
    summarize_clicked = st.button(
        "📝 Summarise",
        use_container_width=True,
    )

with col2:
    explain_clicked = st.button(
        "💡 Explain Simply",
        use_container_width=True,
    )

with col3:
    quiz_clicked = st.button(
        "❓ Generate Quiz",
        use_container_width=True,
    )

if summarize_clicked or explain_clicked or quiz_clicked:
    material = st.session_state.get("study_notes", "").strip()

    if not material:
        st.warning("Please paste your notes or read a PDF first.")
    else:
        if summarize_clicked:
            task = (
                "Summarise these study notes using clear headings and "
                "important exam points. Preserve key definitions and facts."
            )
        elif explain_clicked:
            task = (
                "Explain these study notes in simple English. Explain difficult "
                "terms step by step and give a suitable example where useful."
            )
        else:
            task = (
                "Create 10 practice questions from these notes, with answers "
                "and brief explanations. Include a mix of short-answer and "
                "multiple-choice questions."
            )

        with st.spinner("StudyNova is preparing your study material..."):
            answer = ask_ai(
                f"{task}\n\nSTUDENT'S NOTES:\n{material[:18000]}"
            )

        st.session_state["last_result"] = answer
        st.session_state["last_task"] = task

# ---------------- DISPLAY RESULT ----------------
if st.session_state.get("last_result"):
    st.header("3. Your study result")
    st.markdown(st.session_state["last_result"])

    st.download_button(
        "⬇️ Download result as text",
        data=st.session_state["last_result"],
        file_name="studynova_study_result.txt",
        mime="text/plain",
    )

# ---------------- ASK AI ----------------
st.divider()
st.header("🤖 Ask StudyNova")

question = st.text_area(
    "What would you like help understanding?",
    placeholder="Example: Explain data visualisation with an example.",
    height=100,
)

if st.button("Ask AI", type="primary"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        material = st.session_state.get("study_notes", "").strip()
        prompt = (
            f"Student's question:\n{question.strip()}\n\n"
            f"Relevant study notes:\n{material[:12000] if material else 'No notes supplied.'}\n\n"
            "Answer clearly and help the student understand the topic."
        )

        with st.spinner("StudyNova is thinking..."):
            answer = ask_ai(prompt)

        st.markdown("### Answer")
        st.markdown(answer)

st.divider()
st.caption("StudyNova • Built with Python, Streamlit, and Cloudflare Workers AI")
