# Use official Python image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the supervisor configuration file
COPY supervisord.conf /etc/supervisord.conf


# Run both FastAPI and Streamlit using supervisord
EXPOSE 8000 8501

# Start FastAPI and Streamlit together
CMD uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port 8501 --server.address 0.0.0.0 && wait