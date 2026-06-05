import Fastify from 'fastify'
import cors from '@fastify/cors'
import helmet from '@fastify/helmet'
import rateLimit from '@fastify/rate-limit'
import sensible from '@fastify/sensible'
import { env } from './lib/env.js'
import authPlugin from './plugins/auth.js'

export async function buildServer() {
  const fastify = Fastify({
    logger: {
      level: env.NODE_ENV === 'development' ? 'info' : 'warn',
      ...(env.NODE_ENV === 'development'
        ? { transport: { target: 'pino-pretty', options: { colorize: true } } }
        : {}),
    },
  })

  // Security headers
  await fastify.register(helmet, {
    contentSecurityPolicy: false, // configured separately for API
  })

  // CORS — only allow the frontend origin
  await fastify.register(cors, {
    origin: env.NODE_ENV === 'development' ? true : (env.NEXT_PUBLIC_APP_URL ?? false),
    credentials: true,
  })

  // Rate limiting
  await fastify.register(rateLimit, {
    max: env.RATE_LIMIT_MAX,
    timeWindow: '1 minute',
  })

  // Sensible defaults (error helpers)
  await fastify.register(sensible)

  // Auth plugin
  await fastify.register(authPlugin)

  // Health check — public, no auth
  fastify.get('/health', async () => ({
    status: 'ok',
    environment: env.ENVIRONMENT,
    timestamp: new Date().toISOString(),
  }))

  // Routes will be registered here in later prompts

  return fastify
}
