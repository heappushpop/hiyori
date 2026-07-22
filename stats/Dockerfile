FROM alpine:3.24

RUN addgroup --gid 1000 --system user
RUN adduser --ingroup user --system --uid 1000 user
RUN apk add --no-cache curl

USER user

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
