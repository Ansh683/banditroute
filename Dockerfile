# BanditRoute — containerized for submission.
# Default entrypoint runs the full simulation (no API key required) and
# writes results to /app/output. For the live OpenRouter demo, override
# the command and pass OPENROUTER_API_KEY at `docker run` time.

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

RUN mkdir -p /app/output

# Default: run the simulation end-to-end and generate the dashboard.
CMD ["sh", "-c", "python run_simulation.py && python dashboard.py && cp log.csv dashboard.png /app/output/ && echo 'Done — see /app/output'"]
