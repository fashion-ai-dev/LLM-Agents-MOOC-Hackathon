FROM node:18

WORKDIR /app

COPY . .

RUN cp .env.example .env
RUN npm install && npm run build


FROM nginx:1.21
COPY --from=0 /app/dist /usr/share/nginx/html

EXPOSE 80
