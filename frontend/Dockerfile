FROM node:22-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Copy source
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Install dependencies and run dev server
CMD sh -c "npm install && npm run dev -- --host 0.0.0.0"
