FROM python:3.10.12-slim-bullseye
WORKDIR /app
COPY ./ /app
RUN pip install --upgrade pip
RUN pip install Flask
RUN pip install openai langchain langid markdown
CMD ["python3", "/app/app.py"]
#
# REMOTE
#
#EXPOSE 80
#EXPOSE 443
# 
# LOCAL
#
EXPOSE 8080