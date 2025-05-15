FROM python:3.11

WORKDIR /app
COPY . /app

# Force uninstall + delete old OpenAI SDK and reinstall clean
RUN pip uninstall -y openai && \
    rm -rf /usr/local/lib/python3.11/site-packages/openai* && \
    pip install --no-cache-dir openai==1.14.3

# Install other dependencies (including fixed bcrypt)
RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
