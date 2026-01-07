FROM python:3.14-slim

RUN mkdir -p /app
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["python", "-m", "streamlit", "run", "src/main.py", "--server.address=0.0.0.0", "--browser.serverAddress=localhost"]