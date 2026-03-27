FROM golang:1.26.1-alpine AS builder

WORKDIR /

COPY . /

RUN CGO_ENABLED=0 GOOS=linux go build cmd/server/main.go

FROM alpine:latest

COPY --from=builder /main .

CMD ["./main"]