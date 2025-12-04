FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim AS production
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Copy entrypoint script for runtime env generation
COPY --from=builder /app/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

ENV PORT=3000
EXPOSE 3000

# Use entrypoint to generate runtime env before starting server
ENTRYPOINT ["./entrypoint.sh"]
CMD ["node", "server.js"]
