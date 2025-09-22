# Build stage
FROM docker.io/node:18-slim as build

# Set environment variables to avoid Rollup issues
ENV ROLLUP_WATCH=false
ENV NODE_ENV=production

WORKDIR /app

# Install system dependencies needed for native modules
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./

# Clear npm cache and install all dependencies
RUN npm cache clean --force
RUN npm ci --include=dev

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM docker.io/nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
