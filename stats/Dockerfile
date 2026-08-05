FROM alpine:3.24

RUN <<-EOF
	addgroup --gid 1000 --system user
	adduser --ingroup user --system --uid 1000 user
	apk --cache=no add curl
	EOF

USER user

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
