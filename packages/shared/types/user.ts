// User-related types — mirrors database schema from Prompt 0 Section 0.4

export type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced'
export type RiskAppetite = 'conservative' | 'moderate' | 'aggressive'
export type InvestmentHorizon = 'short_term' | 'medium_term' | 'long_term'
export type PrimaryGoal = 'wealth_creation' | 'regular_income' | 'capital_preservation' | 'learning'

export interface UserProfile {
  id: string
  username: string
  full_name: string | null
  avatar_url: string | null
  experience_level: ExperienceLevel | null
  created_at: string
  updated_at: string
}

export interface UserRiskProfile {
  id: string
  user_id: string
  risk_appetite: RiskAppetite
  investment_horizon: InvestmentHorizon
  primary_goal: PrimaryGoal
  monthly_investment_capacity: string | null
  created_at: string
  updated_at: string
}
