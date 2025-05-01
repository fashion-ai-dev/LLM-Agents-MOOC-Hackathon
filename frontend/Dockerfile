FROM node:20 AS builder

WORKDIR /app

COPY . .

RUN cp .env.example .env

RUN yarn install --frozen-lockfile
RUN yarn build

FROM nginx:1.21

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
