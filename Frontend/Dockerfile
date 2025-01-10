# Stage 1: Build the Angular app using Node.js
FROM node:latest as build

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

# Replace placeholders in environment files
ARG AUTH0_DOMAIN
ARG AUTH0_CLIENT_ID
ARG AUTH0_AUDIENCE

RUN sed -i "s|PLACEHOLDER_AUTH0_DOMAIN|${AUTH0_DOMAIN}|" src/app/environments/environment.ts
RUN sed -i "s|PLACEHOLDER_AUTH0_CLIENT_ID|${AUTH0_CLIENT_ID}|" src/app/environments/environment.ts
RUN sed -i "s|PLACEHOLDER_AUTH0_AUDIENCE|${AUTH0_AUDIENCE}|" src/app/environments/environment.ts

RUN sed -i "s|PLACEHOLDER_AUTH0_DOMAIN|${AUTH0_DOMAIN}|" src/app/environments/environment.prod.ts
RUN sed -i "s|PLACEHOLDER_AUTH0_CLIENT_ID|${AUTH0_CLIENT_ID}|" src/app/environments/environment.prod.ts
RUN sed -i "s|PLACEHOLDER_AUTH0_AUDIENCE|${AUTH0_AUDIENCE}|" src/app/environments/environment.prod.ts

RUN npm run build -- --configuration production

# Stage 2: Serve the Angular app using NGINX
FROM nginx:alpine

COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
