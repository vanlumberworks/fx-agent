# Frontend Dockerfile for Railway deployment
# Multi-stage build for optimized production image

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build the app
RUN pnpm build

# Stage 2: Production
FROM node:20-alpine

WORKDIR /app

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy built files from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./package.json

# Install only production dependencies for serving
# Using vite preview for now (consider switching to 'serve' or nginx for production)
RUN pnpm add vite --prod

# Expose port (Railway will override with $PORT)
EXPOSE 3000

# Start the app
# Note: Railway automatically sets $PORT environment variable
CMD ["sh", "-c", "pnpm vite preview --host 0.0.0.0 --port ${PORT:-3000}"]
