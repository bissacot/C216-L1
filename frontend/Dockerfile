FROM node:24-alpine AS build
WORKDIR /srv/web
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /srv/web/dist /usr/share/nginx/html
EXPOSE 80
