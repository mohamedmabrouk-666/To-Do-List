FROM python:3.13-slim
WORKDIR /app

# Install the application dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# # Copy in the source code
# COPY app.py .
# COPY .env .
# COPY /templates ./templates/

COPY . .

EXPOSE 5000
# --host --> that allow us to create the port to access this application 
# that allow us to   -p 11000:8000  
# without it we must work the default port 
CMD ["python","app.py","--host","0.0.0.0"]