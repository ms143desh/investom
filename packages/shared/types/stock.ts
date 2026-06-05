// Stock-related types — mirrors database schema from Prompt 0 Section 0.4

export type MarketCapCategory = 'large_cap' | 'mid_cap' | 'small_cap' | 'micro_cap'
export type Exchange = 'NSE' | 'BSE' | 'BOTH'
export type CorporateActionType = 'dividend' | 'bonus' | 'split' | 'rights' | 'buyback'

export interface Stock {
  id: string
  ticker_nse: string | null
  ticker_bse: string | null
  company_name: string
  sector: string | null
  industry: string | null
  market_cap_category: MarketCapCategory | null
  exchange: Exchange
  isin: string
  is_active: boolean
  is_fo_eligible: boolean
  index_memberships: string[]
  logo_url: string | null
  website_url: string | null
  created_at: string
  updated_at: string
}

export interface StockPrice {
  id: string
  stock_id: string
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  adjusted_close: number | null
  created_at: string
}

export interface StockFundamentals {
  id: string
  stock_id: string
  period_type: 'annual' | 'quarterly'
  period_end_date: string
  fiscal_year: number | null
  fiscal_quarter: number | null
  revenue: number | null
  ebitda: number | null
  pat: number | null
  eps: number | null
  total_assets: number | null
  total_equity: number | null
  total_debt: number | null
  cash_and_equivalents: number | null
  operating_cash_flow: number | null
  capex: number | null
  dividends_paid: number | null
  shares_outstanding: number | null
  roe: number | null
  roce: number | null
  debt_to_equity: number | null
  current_ratio: number | null
  gross_margin: number | null
  ebitda_margin: number | null
  pat_margin: number | null
  data_source: string | null
  created_at: string
}

export interface CorporateAction {
  id: string
  stock_id: string
  action_type: CorporateActionType
  ex_date: string
  record_date: string | null
  details: Record<string, unknown>
  created_at: string
}

// Assembled response type for the stock overview endpoint
export interface StockOverview {
  stock: Stock
  latest_price: StockPrice | null
  price_change_1d: number | null
  price_change_pct_1d: number | null
  week_52_high: number | null
  week_52_low: number | null
  latest_annual_fundamentals: StockFundamentals | null
  latest_quarterly_fundamentals: StockFundamentals | null
  recent_corporate_actions: CorporateAction[]
  ai_narrative: string | null
}
