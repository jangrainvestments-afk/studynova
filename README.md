# 📚 StudyNova — AI Study Assistant

StudyNova is a Python + Streamlit study assistant that uses Cloudflare Workers AI.

**Live app:** https://jangrainvestments-afk-studynova-streamlit-app-mylywx.streamlit.app/  
**Source code:** https://github.com/jangrainvestments-afk/studynova

## Features

- Upload a text-based PDF and extract selectable text
- Paste or edit study notes
- Summarise notes into key exam points
- Explain difficult material in simple English
- Generate a 10-question practice quiz with answers
- Ask questions about a topic, optionally using the supplied notes
- Download the latest study result as a text file

Scanned PDFs without selectable text may need OCR first.

## Hosting and free-tier expectations

The app is hosted on Streamlit Community Cloud and calls Cloudflare Workers AI.

- Streamlit Community Cloud may put the app to sleep after 12 hours without traffic. A first visit after sleeping may require a wake-up and can take a little time.
- Cloudflare Workers AI currently offers a daily free allocation of 10,000 Neurons. If it is exhausted, AI requests can fail until the daily reset. Neurons are compute units, not the same thing as text tokens.
- Free-tier limits, service policies, and model availability can change. This project cannot guarantee uninterrupted 24/7 availability.
- Do not add a payment method or upgrade a plan just to keep the project working. Check the provider dashboard and current terms first.

## Streamlit Secrets

In Streamlit Community Cloud, open the app's **Settings → Secrets** and add your own values:

```toml
CLOUDFLARE_ACCOUNT_ID = "your_account_id"
CLOUDFLARE_API_TOKEN = "your_api_token"
```

Use the real values in the private Secrets settings only. **Never commit credentials to GitHub or paste them into chat.** The token should have only the permissions required for Workers AI.

## If the app stops working

1. Open the [live app](https://jangrainvestments-afk-studynova-streamlit-app-mylywx.streamlit.app/). If it shows a sleeping page, choose the wake-up option and wait.
2. If the page shows an app error, open the app's **Manage app → Logs** in Streamlit Community Cloud.
3. If the site opens but AI requests fail, check that the two secrets above exist and are non-empty, then check the Cloudflare Workers AI dashboard for quota or service errors.
4. If Cloudflare reports that today's free allocation is exhausted, wait for the daily reset. Do not upgrade or enable billing just to bypass the limit.
5. If a dependency or code change broke the deployment, check the GitHub Actions checks and fix or restore the last working commit.
6. Check [Streamlit Community Cloud status](https://streamlitstatus.com/) for a provider outage.

## Local development

Python 3.11 is selected for deployment compatibility. With [uv](https://docs.astral.sh/uv/):

```bash
uv sync --locked
uv run streamlit run streamlit_app.py
```

The lockfile records resolved dependency versions. To update dependencies intentionally, edit `pyproject.toml`, regenerate `uv.lock`, and test the app before relying on the new deployment.

## Automated checks

GitHub Actions checks that the app's Python syntax is valid and that its declared dependencies can be installed and imported. These checks help catch packaging mistakes; they do not replace testing the live site and AI provider.

## Six-month maintenance checklist

- Keep access to the GitHub, Streamlit Community Cloud, and Cloudflare accounts.
- Never delete the repository, deployment, or required secrets.
- Open the app and test one small AI question before an important demonstration.
- Test PDF extraction, summary, explanation, quiz, and downloads after code/dependency changes.
- Review current free-tier limits and model availability occasionally.
