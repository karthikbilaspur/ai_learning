FROM golang:1.22-alpine AS build
WORKDIR /app
COPY . .
RUN go build -o api
FROM alpine
COPY --from=build /app/api /api
CMD ["/api"]
