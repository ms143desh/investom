// Chat types — mirrors database schema from Prompt 0 Section 0.4

export type ChatRole = 'user' | 'assistant'
export type QueryType =
  | 'stock_qa'
  | 'concept_explanation'
  | 'stock_comparison'
  | 'portfolio_qa'
  | 'market_news'
  | 'general'

export interface ChatConversation {
  id: string
  user_id: string
  title: string | null
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  conversation_id: string
  role: ChatRole
  content: string
  metadata: {
    stocks_mentioned?: string[]
    query_type?: QueryType
  } | null
  token_count: number | null
  created_at: string
}
