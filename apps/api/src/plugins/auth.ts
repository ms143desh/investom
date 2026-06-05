import type { FastifyPluginAsync, FastifyRequest, FastifyReply } from 'fastify'
import fp from 'fastify-plugin'
import { createClient } from '@supabase/supabase-js'
import { env } from '../lib/env.js'

declare module 'fastify' {
  interface FastifyRequest {
    userId: string
  }
}

const authPlugin: FastifyPluginAsync = async (fastify) => {
  fastify.decorate('authenticate', async (request: FastifyRequest, reply: FastifyReply) => {
    const authHeader = request.headers.authorization
    if (!authHeader?.startsWith('Bearer ')) {
      return reply.status(401).send({ error: 'Missing or invalid Authorization header' })
    }

    const token = authHeader.replace('Bearer ', '')
    const supabase = createClient(env.SUPABASE_URL, env.SUPABASE_SECRET_KEY)
    const { data: { user }, error } = await supabase.auth.getUser(token)

    if (error || !user) {
      return reply.status(401).send({ error: 'Unauthorized' })
    }

    request.userId = user.id
  })
}

declare module 'fastify' {
  interface FastifyInstance {
    authenticate: (request: FastifyRequest, reply: FastifyReply) => Promise<void>
  }
}

export default fp(authPlugin, { name: 'auth' })
