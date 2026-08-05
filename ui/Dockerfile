FROM python:3-alpine

RUN <<-EOF
	addgroup --gid 1000 --system user
	adduser --ingroup user --system --uid 1000 user
	apk --cache=no add curl
	mkdir /static
	chown user:user /static
	EOF

USER user

ARG WORKDIR=/usr/src/app

ENV PATH="$WORKDIR/.venv/bin:$PATH"
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="$WORKDIR/src/ui:$WORKDIR/src/xraygrpcapi:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1

WORKDIR "$WORKDIR"

COPY . .

RUN <<-EOF
	mkdir db
	python -m venv .venv
	pip install .
	EOF

ENTRYPOINT ["./entrypoint.sh"]

CMD daphne --bind 0.0.0.0 --port "$UI_PORT" ui.asgi:application
