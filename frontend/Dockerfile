FROM node:24-slim

WORKDIR /app

# Las dependencias se copian primero: así Docker no las reinstala
# cada vez que cambia el código.
COPY package.json package-lock.json .npmrc ./
RUN npm ci

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
