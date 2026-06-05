// Alert and notification types — mirrors database schema from Prompt 0 Section 0.4

export type AlertType = 'price_above' | 'price_below'
export type NotificationType = 'price_alert' | 'system'

export interface PriceAlert {
  id: string
  user_id: string
  stock_id: string
  alert_type: AlertType
  target_price: number
  is_active: boolean
  is_triggered: boolean
  triggered_at: string | null
  triggered_price: number | null
  created_at: string
}

export interface Notification {
  id: string
  user_id: string
  type: NotificationType
  title: string
  body: string
  metadata: Record<string, unknown> | null
  is_read: boolean
  created_at: string
}
