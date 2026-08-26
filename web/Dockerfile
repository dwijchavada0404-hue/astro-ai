FROM node:22-alpine AS build

WORKDIR /app

ARG VITE_ASTROAI_API_URL
ARG VITE_OIDC_AUTHORITY
ARG VITE_OIDC_CLIENT_ID
ARG VITE_OIDC_SCOPE
ARG VITE_OIDC_AUDIENCE

# Vite substitutes VITE_* values while creating the static bundle. Railway
# service variables are available at runtime by default, so promote the
# public, non-secret client settings into this build stage explicitly.
ENV VITE_ASTROAI_API_URL=${VITE_ASTROAI_API_URL} \
    VITE_OIDC_AUTHORITY=${VITE_OIDC_AUTHORITY} \
    VITE_OIDC_CLIENT_ID=${VITE_OIDC_CLIENT_ID} \
    VITE_OIDC_SCOPE=${VITE_OIDC_SCOPE} \
    VITE_OIDC_AUDIENCE=${VITE_OIDC_AUDIENCE}

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
