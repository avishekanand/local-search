FROM --platform=linux/arm64 node:18-alpine

WORKDIR /usr/src/app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend/ ./

EXPOSE 3000
CMD ["npm", "start"]
