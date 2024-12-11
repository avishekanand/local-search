FROM --platform=linux/arm64 node:18-alpine

WORKDIR /usr/src/app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend/ ./

EXPOSE 3000

# Set the OpenSSL legacy provider option
ENV NODE_OPTIONS="--openssl-legacy-provider"

CMD ["npm", "start"]
