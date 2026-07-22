FROM python:3-alpine

ARG WORKDIR=/usr/src/app

ENV PATH="$WORKDIR/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="$WORKDIR/xray/grpc"
ENV PYTHONUNBUFFERED=1

RUN addgroup --gid 1000 --system user
RUN adduser --ingroup user --system --uid 1000 user
RUN apk add --no-cache curl
RUN mkdir /static
RUN chown user:user /static

USER user

WORKDIR "$WORKDIR"

COPY requirements.txt .

RUN mkdir db
RUN python -m venv .venv
RUN pip --no-cache-dir install --requirement requirements.txt

COPY . .

HEALTHCHECK --start-period=30s CMD curl --fail --header "Host: $DOMAIN_NAME" "ui:$UI_PORT" || exit 1

ENTRYPOINT ["./entrypoint.sh"]

CMD daphne --bind 0.0.0.0 --port "$UI_PORT" ui.asgi:application
