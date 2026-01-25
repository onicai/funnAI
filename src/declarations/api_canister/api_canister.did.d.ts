import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export type AdminRole = { 'AdminQuery' : null } |
  { 'AdminUpdate' : null };
export interface AdminRoleAssignment {
  'principal' : string,
  'assignedAt' : bigint,
  'assignedBy' : string,
  'note' : string,
  'role' : AdminRole,
}
export type AdminRoleAssignmentResult = { 'Ok' : AdminRoleAssignment } |
  { 'Err' : ApiError };
export type AdminRoleAssignmentsResult = { 'Ok' : Array<AdminRoleAssignment> } |
  { 'Err' : ApiError };
export interface ApiCanister {
  'amiController' : ActorMethod<[], AuthRecordResult>,
  'assignAdminRole' : ActorMethod<
    [AssignAdminRoleInputRecord],
    AdminRoleAssignmentResult
  >,
  'bulkCreateDailyMetricsAdmin' : ActorMethod<
    [Array<DailyMetricInput>],
    NatResult
  >,
  'createDailyMetricAdmin' : ActorMethod<[DailyMetricInput], DailyMetricResult>,
  'deleteDailyMetricAdmin' : ActorMethod<[string], NatResult>,
  'getAdminRoles' : ActorMethod<[], AdminRoleAssignmentsResult>,
  'getDailyMetricByDate' : ActorMethod<[string], DailyMetricResult>,
  'getDailyMetrics' : ActorMethod<
    [[] | [DailyMetricsQuery]],
    DailyMetricsResult
  >,
  'getDailyMetricsAdmin' : ActorMethod<[], DailyMetricsResult>,
  'getLatestDailyMetric' : ActorMethod<[], DailyMetricResult>,
  'getMasterCanisterId' : ActorMethod<[], AuthRecordResult>,
  'getNumDailyMetrics' : ActorMethod<[], NatResult>,
  'getTokenRewardsData' : ActorMethod<[], TokenRewardsDataResult>,
  'health' : ActorMethod<[], StatusCodeRecordResult>,
  'resetDailyMetricsAdmin' : ActorMethod<[], NatResult>,
  'revokeAdminRole' : ActorMethod<[string], TextResult>,
  'setMasterCanisterId' : ActorMethod<[string], AuthRecordResult>,
  'updateDailyMetricAdmin' : ActorMethod<
    [UpdateDailyMetricAdminInput],
    DailyMetricResult
  >,
  'whoami' : ActorMethod<[], Principal>,
}
export type ApiError = { 'FailedOperation' : null } |
  { 'InvalidId' : null } |
  { 'ZeroAddress' : null } |
  { 'Unauthorized' : null } |
  { 'StatusCode' : StatusCode } |
  { 'Other' : string } |
  { 'InsuffientCycles' : bigint };
export interface AssignAdminRoleInputRecord {
  'principal' : string,
  'note' : string,
  'role' : AdminRole,
}
export interface AuthRecord { 'auth' : string }
export type AuthRecordResult = { 'Ok' : AuthRecord } |
  { 'Err' : ApiError };
export interface DailyBurnRate { 'usd' : number, 'cycles' : bigint }
export interface DailyMetric {
  'derived_metrics' : DerivedMetrics,
  'mainers' : MainersMetrics,
  'metadata' : DailyMetricMetadata,
  'system_metrics' : SystemMetrics,
}
export interface DailyMetricInput {
  'total_paused_mainers' : bigint,
  'date' : string,
  'paused_very_high_burn_rate_mainers' : bigint,
  'paused_medium_burn_rate_mainers' : bigint,
  'total_cycles_all_mainers' : bigint,
  'paused_custom_burn_rate_mainers' : bigint,
  'active_very_high_burn_rate_mainers' : bigint,
  'active_high_burn_rate_mainers' : bigint,
  'active_low_burn_rate_mainers' : bigint,
  'paused_low_burn_rate_mainers' : bigint,
  'daily_burn_rate_usd' : number,
  'paused_high_burn_rate_mainers' : bigint,
  'total_active_mainers' : bigint,
  'active_medium_burn_rate_mainers' : bigint,
  'active_custom_burn_rate_mainers' : bigint,
  'daily_burn_rate_cycles' : bigint,
  'funnai_index' : number,
  'total_mainers_created' : bigint,
}
export interface DailyMetricMetadata {
  'updated_at' : string,
  'date' : string,
  'created_at' : string,
}
export type DailyMetricResult = { 'Ok' : DailyMetric } |
  { 'Err' : ApiError };
export interface DailyMetricUpdateInput {
  'total_paused_mainers' : [] | [bigint],
  'paused_very_high_burn_rate_mainers' : [] | [bigint],
  'paused_medium_burn_rate_mainers' : [] | [bigint],
  'total_cycles_all_mainers' : [] | [bigint],
  'paused_custom_burn_rate_mainers' : [] | [bigint],
  'active_very_high_burn_rate_mainers' : [] | [bigint],
  'active_high_burn_rate_mainers' : [] | [bigint],
  'active_low_burn_rate_mainers' : [] | [bigint],
  'paused_low_burn_rate_mainers' : [] | [bigint],
  'daily_burn_rate_usd' : [] | [number],
  'paused_high_burn_rate_mainers' : [] | [bigint],
  'total_active_mainers' : [] | [bigint],
  'active_medium_burn_rate_mainers' : [] | [bigint],
  'active_custom_burn_rate_mainers' : [] | [bigint],
  'daily_burn_rate_cycles' : [] | [bigint],
  'funnai_index' : [] | [number],
  'total_mainers_created' : [] | [bigint],
}
export interface DailyMetricsQuery {
  'end_date' : [] | [string],
  'limit' : [] | [bigint],
  'start_date' : [] | [string],
}
export interface DailyMetricsResponse {
  'period' : PeriodInfo,
  'daily_metrics' : Array<DailyMetric>,
}
export type DailyMetricsResult = { 'Ok' : DailyMetricsResponse } |
  { 'Err' : ApiError };
export interface DerivedMetrics {
  'avg_cycles_per_mainer' : number,
  'paused_percentage' : number,
  'tier_distribution' : {
    'low' : number,
    'custom' : number,
    'high' : number,
    'very_high' : number,
    'medium' : number,
  },
  'burn_rate_per_active_mainer' : number,
  'active_percentage' : number,
}
export interface MainersMetrics {
  'totals' : {
    'created' : bigint,
    'active' : bigint,
    'total_cycles' : bigint,
    'paused' : bigint,
  },
  'breakdown_by_tier' : {
    'active' : MainersTierBreakdown,
    'paused' : MainersTierBreakdown,
  },
}
export interface MainersTierBreakdown {
  'low' : bigint,
  'custom' : bigint,
  'high' : bigint,
  'very_high' : bigint,
  'medium' : bigint,
}
export type NatResult = { 'Ok' : bigint } |
  { 'Err' : ApiError };
export interface PeriodInfo {
  'end_date' : string,
  'total_days' : bigint,
  'start_date' : string,
}
export type StatusCode = number;
export interface StatusCodeRecord { 'status_code' : StatusCode }
export type StatusCodeRecordResult = { 'Ok' : StatusCodeRecord } |
  { 'Err' : ApiError };
export interface SystemMetrics {
  'funnai_index' : number,
  'daily_burn_rate' : DailyBurnRate,
  'total_cycles_protocol' : bigint,
  'total_cycles_protocol_usd' : number,
}
export type TextResult = { 'Ok' : string } |
  { 'Err' : ApiError };
export interface TokenRewardsData {
  'metadata' : TokenRewardsMetadata,
  'data' : Array<TokenRewardsEntry>,
}
export type TokenRewardsDataResult = { 'Ok' : TokenRewardsData } |
  { 'Err' : ApiError };
export interface TokenRewardsEntry {
  'date' : string,
  'quarter' : string,
  'rewards_per_challenge' : number,
  'total_minted' : number,
  'notes' : string,
  'rewards_per_quarter' : number,
}
export interface TokenRewardsMetadata {
  'dataset' : string,
  'description' : string,
  'last_updated' : string,
  'version' : string,
  'units' : { 'rewards_per_challenge' : string, 'total_minted' : string },
}
export interface UpdateDailyMetricAdminInput {
  'date' : string,
  'input' : DailyMetricUpdateInput,
}
export interface _SERVICE extends ApiCanister {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
