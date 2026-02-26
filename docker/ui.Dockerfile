FROM node:20-alpine AS build
WORKDIR /ui

COPY jarvis-ui/package.json /ui/package.json
RUN npm install

COPY jarvis-ui /ui
RUN npm run build

FROM nginx:1.27-alpine AS runtime

RUN addgroup -S jarvis && adduser -S -G jarvis jarvis && \
    mkdir -p /var/cache/nginx /var/run /usr/share/nginx/html && \
    chown -R jarvis:jarvis /var/cache/nginx /var/run /usr/share/nginx/html

COPY --from=build /ui/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

USER jarvis
EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:5173/ >/dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
