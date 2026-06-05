// Watchlist types — mirrors database schema from Prompt 0 Section 0.4

export interface Watchlist {
  id: string
  user_id: string
  name: string
  created_at: string
}

export interface WatchlistItem {
  id: string
  watchlist_id: string
  stock_id: string
  noted_price: number | null
  user_notes: string | null
  price_target: number | null
  added_at: string
}
