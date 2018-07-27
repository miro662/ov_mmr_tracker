FROM 'python:3.7'
ENV PYTHONUNBUFFERED 1

# Create directory for code and copy data there
RUN mkdir /code
WORKDIR /code
COPY . /code

# Install pipenv and install requirements from Pipfile
RUN pip install pipenv
RUN pipenv install --system --deploy

# Make app use Docker-specific config
ENV DJANGO_SETTINGS_MODULE ov_mmr_tracker.docker_settings

# Run app (using gunicorn)
EXPOSE 8000/tcp
CMD ["gunicorn", "-b 0.0.0.0:8000" , "ov_mmr_tracker.wsgi"]