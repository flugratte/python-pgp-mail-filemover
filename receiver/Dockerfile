FROM python:3.8

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /certs

ENV UID=1000
ENV GID=1000

RUN groupadd -g $GID appuser \
    && useradd -r -u $UID -g $GID appuser \
    && mkdir -p /home/appuser/.gnupg \
    && chown -R appuser:appuser /home/appuser \
    && (chmod 600 /home/appuser/.gnupg/* || true)\
    && chmod 700 /home/appuser/.gnupg

RUN mkdir -p /attachments \
    && chown -R appuser:appuser /attachments
USER appuser

CMD ["python", "-u", "receive-mail.py"]