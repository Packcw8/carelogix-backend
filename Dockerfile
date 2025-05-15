WORKDIR /app
COPY . /app

# 🧼 Force uninstall + wipe any old OpenAI SDK and reinstall clean
RUN pip uninstall -y openai && \
    rm -rf /usr/local/lib/python3.11/site-packages/openai* && \
    pip install --no-cache-dir openai==1.14.3

# 📦 Install dependencies including fixed bcrypt
RUN pip install --upgrade pip && pip install -r requirements.txt
