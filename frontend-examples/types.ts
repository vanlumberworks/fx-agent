/**
 * TypeScript Type Definitions for Forex Agent System Streaming API
 *
 * These types define the structure of all events emitted by the streaming API.
 * Use these in your TypeScript/React/Vue/Angular frontend applications.
 *
 * @version 2.0.0
 */

// ============================================================================
// Base Types
// ============================================================================

export type ActionType = 'BUY' | 'SELL' | 'WAIT';

export type AssetType = 'forex' | 'commodity' | 'crypto';

export type AgentName = 'news' | 'technical' | 'fundamental';

export type EventType =
  | 'start'
  | 'query_parsed'
  | 'agent_update'
  | 'risk_update'
  | 'decision'
  | 'complete'
  | 'error';

// ============================================================================
// Query Context
// ============================================================================

export interface QueryContext {
  pair: string;
  asset_type: AssetType;
  base_currency: string;
  quote_currency: string;
  timeframe: string;
  user_intent: string;
  risk_tolerance: string;
  additional_context?: Record<string, any>;
}

// ============================================================================
// Agent Results
// ============================================================================

export interface AgentResult<T = any> {
  success: boolean;
  data?: T;
  summary?: string;
  error?: string;
}

export interface NewsData {
  sentiment: string;
  score: number;
  confidence: number;
  headlines: Array<{
    title: string;
    source: string;
    sentiment: string;
    published: string;
  }>;
}

export interface TechnicalData {
  trend: string;
  strength: number;
  indicators: {
    rsi: number;
    macd: {
      value: number;
      signal: number;
      histogram: number;
    };
    moving_averages: {
      sma_20: number;
      sma_50: number;
      sma_200: number;
      ema_12: number;
      ema_26: number;
    };
  };
  support_resistance: {
    support_levels: number[];
    resistance_levels: number[];
  };
}

export interface FundamentalData {
  economic_outlook: string;
  strength_comparison: {
    base_currency: number;
    quote_currency: number;
  };
  key_factors: {
    gdp_growth: Record<string, number>;
    interest_rates: Record<string, number>;
    inflation: Record<string, number>;
    unemployment: Record<string, number>;
  };
}

export interface RiskData {
  trade_approved: boolean;
  rejection_reason?: string;
  position_size: number;
  risk_amount: number;
  risk_percentage: number;
  stop_loss_pips: number;
  take_profit_pips: number;
  risk_reward_ratio: number;
  analysis: string;
}

// ============================================================================
// Decision & Trade Parameters
// ============================================================================

export interface TradeParameters {
  entry_price: string;
  stop_loss: string;
  take_profit: string;
  position_size: number;
}

export interface GroundingSource {
  title: string;
  url: string;
  snippet?: string;
}

export interface GroundingMetadata {
  search_queries: string[];
  sources: GroundingSource[];
  grounding_score?: number;
}

export interface DecisionReasoning {
  summary: string;
  web_verification?: string;
  key_factors: string[];
  risks?: string[];
  risk_rejection?: boolean;
}

export interface Decision {
  action: ActionType;
  confidence: number;
  reasoning: DecisionReasoning;
  trade_parameters?: TradeParameters;
  grounding_metadata?: GroundingMetadata;
}

// ============================================================================
// Complete Analysis Result
// ============================================================================

export interface AgentResults {
  news: AgentResult<NewsData> | null;
  technical: AgentResult<TechnicalData> | null;
  fundamental: AgentResult<FundamentalData> | null;
  risk: AgentResult<RiskData> | null;
}

export interface AnalysisMetadata {
  steps: number;
  errors: Record<string, string> | null;
}

export interface AnalysisResult {
  user_query: string;
  query_context: QueryContext | null;
  pair: string | null;
  decision: Decision | null;
  agent_results: AgentResults;
  metadata: AnalysisMetadata;
}

// ============================================================================
// SSE Event Data Types
// ============================================================================

export interface StartEventData {
  query: string;
  timestamp: string;
}

export interface QueryParsedEventData {
  step: number;
  query_context: QueryContext;
  pair: string;
  timestamp: string;
}

export interface AgentUpdateEventData {
  step: number;
  agent: AgentName;
  result: AgentResult;
  timestamp: string;
}

export interface RiskUpdateEventData {
  step: number;
  risk_result: AgentResult<RiskData>;
  trade_approved: boolean;
  timestamp: string;
}

export interface DecisionEventData {
  step: number;
  decision: Decision;
  timestamp: string;
}

export interface CompleteEventData {
  result: AnalysisResult;
  timestamp: string;
}

export interface ErrorEventData {
  error: string;
  error_type: string;
  timestamp: string;
}

// ============================================================================
// SSE Event Union Type
// ============================================================================

export type StreamEventData =
  | StartEventData
  | QueryParsedEventData
  | AgentUpdateEventData
  | RiskUpdateEventData
  | DecisionEventData
  | CompleteEventData
  | ErrorEventData;

export interface StreamEvent<T extends StreamEventData = StreamEventData> {
  event: EventType;
  data: T;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface AnalysisRequest {
  query: string;
  account_balance?: number;
  max_risk_per_trade?: number;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  version: string;
  api_configured: boolean;
  error?: string;
}

export interface SystemInfo {
  system: {
    account_balance: number;
    max_risk_per_trade: number;
    api_configured: boolean;
  };
  workflow: {
    nodes: string[];
    edges: Array<[string, string]>;
    num_nodes: number;
    num_edges: number;
  };
}

// ============================================================================
// Event Handler Types
// ============================================================================

export type EventHandler<T extends StreamEventData = StreamEventData> = (
  data: T
) => void;

export interface EventHandlers {
  onStart?: EventHandler<StartEventData>;
  onQueryParsed?: EventHandler<QueryParsedEventData>;
  onAgentUpdate?: EventHandler<AgentUpdateEventData>;
  onRiskUpdate?: EventHandler<RiskUpdateEventData>;
  onDecision?: EventHandler<DecisionEventData>;
  onComplete?: EventHandler<CompleteEventData>;
  onError?: EventHandler<ErrorEventData>;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Type guard to check if event is of a specific type
 */
export function isEventType<T extends EventType>(
  event: EventType,
  type: T
): event is T {
  return event === type;
}

/**
 * Type guard for checking if decision is a trade decision (BUY/SELL)
 */
export function isTradeDecision(decision: Decision): boolean {
  return decision.action === 'BUY' || decision.action === 'SELL';
}

/**
 * Type guard for checking if risk is approved
 */
export function isRiskApproved(riskData: RiskData): boolean {
  return riskData.trade_approved === true;
}
