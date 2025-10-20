FROM node:20-alpine as build
WORKDIR /app
COPY package.json vite.config.js /app/
COPY src /app/src
RUN npm install && npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]