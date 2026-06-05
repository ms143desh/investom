// env validation runs first — will exit(1) if any required var is missing
import './lib/env.js'
import { env } from './lib/env.js'
import { buildServer } from './server.js'

const start = async () => {
  const fastify = await buildServer()

  try {
    await fastify.listen({ port: env.PORT, host: '0.0.0.0' })
    fastify.log.info(`Server running on port ${env.PORT} [${env.ENVIRONMENT}]`)
  } catch (err) {
    fastify.log.error(err)
    process.exit(1)
  }
}

start()
