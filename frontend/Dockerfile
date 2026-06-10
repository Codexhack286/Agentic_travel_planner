# Stage 1: Building the Next.js production bundle
FROM node:18-alpine AS builder
WORKDIR /app

# Copy package config and lockfile
COPY package*.json ./
RUN npm ci

# Copy frontend source files
COPY . .

# Set API endpoint build arg
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Run build script
RUN npm run build

# Stage 2: Clean production runner
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copy build output and packages
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

# Start next server
CMD ["npm", "run", "start"]
