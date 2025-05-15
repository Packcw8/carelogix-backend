FROM python:3.11

WORKDIR /app
COPY . /app

# 🔥 Force uninstall any old version of OpenAI, then clean-install the right one
RUN pip uninstall -y openai && pip install --no-cache-dir openai==1.14.3

# 🧱 Install remaining dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# ✅ Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
