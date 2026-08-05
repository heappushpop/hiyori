FROM python:3-alpine

RUN <<-EOF
	addgroup --gid 1000 --system user
	adduser --ingroup user --system --uid 1000 user
	apk --cache=no add curl
	mkdir /db /static /xray
	chown user:user /db /static /xray
	EOF

USER user

ARG WORKDIR=/usr/src/app

ENV PATH="$WORKDIR/.venv/bin:$PATH"
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="$WORKDIR/src/ui:$WORKDIR/src/xraygrpcapi:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1

WORKDIR "$WORKDIR"

COPY pyproject.toml .

RUN <<-EOF
	python -m venv .venv
	pip install .
	EOF

COPY . .

ENTRYPOINT ["./entrypoint.sh"]

CMD daphne --bind 0.0.0.0 --port "$UI_PORT" ui.asgi:application
