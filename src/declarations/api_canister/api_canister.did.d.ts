import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export interface ActivityFeedQuery {
  'challengesLimit' : [] | [bigint],
  'sinceTimestamp' : [] | [bigint],
  'winnersOffset' : [] | [bigint],
  'challengesOffset' : [] | [bigint],
  'winnersLimit' : [] | [bigint],
}
export interface ActivityFeedResponse {
  'totalWinners' : bigint,
  'cacheTimestamp' : bigint,
  'totalChallenges' : bigint,
  'challenges' : Array<Challenge>,
  'winners' : Array<ChallengeWinnerDeclarationArray>,
}
export type ActivityFeedResult = { 'Ok' : ActivityFeedResponse } |
  { 'Err' : ApiError };
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
  /**
   * / Get recent protocol activity with independent pagination
   */
  'getActivityFeed' : ActorMethod<[ActivityFeedQuery], ActivityFeedResult>,
  /**
   * / Get cache status for monitoring
   */
  'getActivityFeedCacheStatus' : ActorMethod<[], CacheStatusResult>,
  'getActivityFeedSyncIntervalAdmin' : ActorMethod<[], NatResult>,
  'getAdminRoles' : ActorMethod<[], AdminRoleAssignmentsResult>,
  'getDailyMetricByDate' : ActorMethod<[string], DailyMetricResult>,
  'getDailyMetrics' : ActorMethod<
    [[] | [DailyMetricsQuery]],
    DailyMetricsResult
  >,
  'getDailyMetricsAdmin' : ActorMethod<[], DailyMetricsResult>,
  'getDailyMetricsRunStatusAdmin' : ActorMethod<[], Result>,
  'getLatestDailyMetric' : ActorMethod<[], DailyMetricResult>,
  'getMasterCanisterId' : ActorMethod<[], AuthRecordResult>,
  'getNumDailyMetrics' : ActorMethod<[], NatResult>,
  /**
   * / Get current open challenges from cache
   */
  'getOpenChallengesFromCache' : ActorMethod<[], ChallengesResult>,
  'getPricingCacheAdmin' : ActorMethod<[], PricingCacheResult>,
  'getShareServiceCanisterIdAdmin' : ActorMethod<[], AuthRecordResult>,
  'getTokenIndexCanisterIdAdmin' : ActorMethod<[], AuthRecordResult>,
  'getTokenRewardsData' : ActorMethod<[], TokenRewardsDataResult>,
  'getTotalBurned' : ActorMethod<[], TotalBurnedResult>,
  'health' : ActorMethod<[], StatusCodeRecordResult>,
  'previewDailyMetricsAggregationAdmin' : ActorMethod<[], DailyMetricResult>,
  'previewIsoDateAdmin' : ActorMethod<[bigint], TextResult>,
  'pricingTransform' : ActorMethod<
    [{ 'context' : Uint8Array | number[], 'response' : http_request_result }],
    http_request_result
  >,
  'pullShareServiceSnapshotAdmin' : ActorMethod<
    [],
    ShareAgentRegistryWithActivityResult
  >,
  'resetDailyMetricsAdmin' : ActorMethod<[], NatResult>,
  'revokeAdminRole' : ActorMethod<[string], TextResult>,
  'setActivityFeedSyncIntervalAdmin' : ActorMethod<
    [bigint],
    StatusCodeRecordResult
  >,
  'setMasterCanisterId' : ActorMethod<[string], AuthRecordResult>,
  'setShareServiceCanisterIdAdmin' : ActorMethod<[string], AuthRecordResult>,
  'setTokenIndexCanisterIdAdmin' : ActorMethod<[string], AuthRecordResult>,
  'startActivityFeedTimerAdmin' : ActorMethod<[], AuthRecordResult>,
  'startBurnScanTimerAdmin' : ActorMethod<[], AuthRecordResult>,
  'startDailyMetricsTimerAdmin' : ActorMethod<[], AuthRecordResult>,
  'startPricingTimerAdmin' : ActorMethod<[], AuthRecordResult>,
  'stopActivityFeedTimerAdmin' : ActorMethod<[], AuthRecordResult>,
  'stopBurnScanTimerAdmin' : ActorMethod<[], AuthRecordResult>,
  'stopDailyMetricsTimerAdmin' : ActorMethod<[], AuthRecordResult>,
  'stopPricingTimerAdmin' : ActorMethod<[], AuthRecordResult>,
  'triggerBurnScanAdmin' : ActorMethod<[], AuthRecordResult>,
  'triggerDailyMetricsAggregationAdmin' : ActorMethod<[], DailyMetricResult>,
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
export interface CacheStatus {
  'syncIntervalSeconds' : bigint,
  'cachedChallengesCount' : bigint,
  'lastSyncTimestamp' : bigint,
  'cachedWinnersCount' : bigint,
}
export type CacheStatusResult = { 'Ok' : CacheStatus } |
  { 'Err' : ApiError };
export type CanisterAddress = string;
export type CanisterStatus = { 'Paused' : null } |
  { 'Paid' : null } |
  { 'Unlocked' : null } |
  { 'LlmSetupFinished' : null } |
  { 'ControllerCreated' : null } |
  { 'LlmSetupInProgress' : LlmSetupStatus } |
  { 'Running' : null } |
  { 'Other' : string } |
  { 'ControllerCreationInProgress' : null };
export interface Challenge {
  'challengeClosedTimestamp' : [] | [bigint],
  'challengeTopicStatus' : ChallengeTopicStatus,
  'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : bigint,
  'protocolOperationFeesCut' : bigint,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeCreationTimestamp' : bigint,
  'challengeCreatedBy' : CanisterAddress,
  'challengeTopicId' : string,
  'cyclesGenerateResponseOwnctrlOwnllmHIGH' : bigint,
  'cyclesGenerateResponseOwnctrlOwnllmLOW' : bigint,
  'mainerPromptId' : string,
  'cyclesGenerateResponseSsctrlSsllm' : bigint,
  'mainerMaxContinueLoopCount' : bigint,
  'mainerTemp' : number,
  'challengeStatus' : ChallengeStatus,
  'cyclesGenerateResponseOwnctrlGs' : bigint,
  'challengeQuestionSeed' : number,
  'mainerNumTokens' : bigint,
  'challengeQuestion' : string,
  'challengeId' : string,
  'challengeTopic' : string,
  'cyclesGenerateChallengeChctrlChllm' : bigint,
  'cyclesGenerateResponseSactrlSsctrl' : bigint,
  'judgePromptId' : string,
  'cyclesSubmitResponse' : bigint,
  'cyclesGenerateChallengeGsChctrl' : bigint,
  'cyclesGenerateResponseSsctrlGs' : bigint,
}
export interface ChallengeParticipantEntry {
  'result' : ChallengeParticipationResult,
  'reward' : ChallengeWinnerReward,
  'ownedBy' : Principal,
  'submittedBy' : Principal,
  'submissionId' : string,
}
export type ChallengeParticipationResult = { 'ThirdPlace' : null } |
  { 'SecondPlace' : null } |
  { 'Winner' : null } |
  { 'Other' : string } |
  { 'Participated' : null };
export type ChallengeStatus = { 'Open' : null } |
  { 'Closed' : null } |
  { 'Archived' : null } |
  { 'Other' : string };
export type ChallengeTopicStatus = { 'Open' : null } |
  { 'Closed' : null } |
  { 'Archived' : null } |
  { 'Other' : string };
export interface ChallengeWinnerDeclarationArray {
  'participants' : Array<ChallengeParticipantEntry>,
  'thirdPlace' : ChallengeParticipantEntry,
  'winner' : ChallengeParticipantEntry,
  'secondPlace' : ChallengeParticipantEntry,
  'finalizedTimestamp' : bigint,
  'challengeId' : string,
}
export interface ChallengeWinnerReward {
  'distributed' : boolean,
  'rewardDetails' : string,
  'rewardType' : RewardType,
  'amount' : bigint,
  'distributedTimestamp' : [] | [bigint],
}
export type ChallengesResult = { 'Ok' : Array<Challenge> } |
  { 'Err' : ApiError };
export interface CycleAmount { 'usd' : number, 'cycles' : bigint }
export interface CyclesBurnRate {
  'cycles' : bigint,
  'timeInterval' : TimeInterval,
}
export type CyclesBurnRateDefault = { 'Low' : null } |
  { 'Mid' : null } |
  { 'VeryHigh' : null } |
  { 'High' : null } |
  { 'Custom' : CyclesBurnRate };
export interface DailyBurnRate { 'usd' : number, 'cycles' : bigint }
export interface DailyMetric {
  'derived_metrics' : DerivedMetrics,
  'mainers' : MainersMetrics,
  'metadata' : DailyMetricMetadata,
  'system_metrics' : SystemMetrics,
}
export interface DailyMetricInput {
  'total_paused_mainers' : bigint,
  'total_cycles_all_usd' : [] | [number],
  'total_cycles_protocol' : [] | [bigint],
  'total_cycles_mainers_usd' : [] | [number],
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
  'total_cycles_all' : [] | [bigint],
  'active_medium_burn_rate_mainers' : bigint,
  'active_custom_burn_rate_mainers' : bigint,
  'daily_burn_rate_cycles' : bigint,
  'funnai_index' : number,
  'total_mainers_created' : bigint,
  'total_cycles_protocol_usd' : [] | [number],
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
  'total_cycles_all_usd' : [] | [number],
  'total_cycles_protocol' : [] | [bigint],
  'total_cycles_mainers_usd' : [] | [number],
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
  'total_cycles_all' : [] | [bigint],
  'active_medium_burn_rate_mainers' : [] | [bigint],
  'active_custom_burn_rate_mainers' : [] | [bigint],
  'daily_burn_rate_cycles' : [] | [bigint],
  'funnai_index' : [] | [number],
  'total_mainers_created' : [] | [bigint],
  'total_cycles_protocol_usd' : [] | [number],
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
export interface DailyMetricsRunStatus {
  'lastFailureMessage' : [] | [string],
  'timerActive' : boolean,
  'lastSuccessfulMetricDate' : [] | [string],
}
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
export type LlmSetupStatus = { 'CodeInstallInProgress' : null } |
  { 'CanisterCreated' : null } |
  { 'ConfigurationInProgress' : null } |
  { 'CanisterCreationInProgress' : null } |
  { 'ModelUploadProgress' : number };
export type MainerAgentCanisterType = { 'NA' : null } |
  { 'Own' : null } |
  { 'ShareAgent' : null } |
  { 'ShareService' : null };
export interface MainerConfigurationInput {
  'selectedLLM' : [] | [SelectableMainerLLMs],
  'subnetLlm' : string,
  'mainerAgentCanisterType' : MainerAgentCanisterType,
  'cyclesForMainer' : bigint,
  'subnetCtrl' : string,
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
export interface OfficialMainerAgentCanister {
  'status' : CanisterStatus,
  'canisterType' : ProtocolCanisterType,
  'ownedBy' : Principal,
  'creationTimestamp' : bigint,
  'createdBy' : Principal,
  'mainerConfig' : MainerConfigurationInput,
  'subnet' : string,
  'address' : CanisterAddress,
}
export interface PeriodInfo {
  'end_date' : string,
  'total_days' : bigint,
  'start_date' : string,
}
export interface PricingCache {
  'xdrPermyriadPerIcp' : bigint,
  'lastUpdatedNs' : bigint,
  'icApiTcycleBurnRatePerDay' : number,
  'usdPerComputedXdr' : number,
}
export type PricingCacheResult = { 'Ok' : PricingCache } |
  { 'Err' : ApiError };
export type ProtocolCanisterType = { 'MainerAgent' : MainerAgentCanisterType } |
  { 'MainerLlm' : null } |
  { 'Challenger' : null } |
  { 'Judge' : null } |
  { 'Verifier' : null } |
  { 'MainerCreator' : null };
export type Result = { 'Ok' : DailyMetricsRunStatus } |
  { 'Err' : ApiError };
export type RewardType = { 'ICP' : null } |
  { 'Coupon' : string } |
  { 'MainerToken' : null } |
  { 'Cycles' : null } |
  { 'Other' : string };
export type SelectableMainerLLMs = { 'Qwen2_5_500M' : null };
export interface ShareAgentActivity {
  'cycleBalance' : bigint,
  'cyclesBurnRate' : CyclesBurnRateDefault,
  'address' : string,
  'lastChallengeRequestTimestamp' : bigint,
}
export interface ShareAgentRegistryWithActivity {
  'registry' : Array<OfficialMainerAgentCanister>,
  'activity' : Array<ShareAgentActivity>,
}
export type ShareAgentRegistryWithActivityResult = {
    'Ok' : ShareAgentRegistryWithActivity
  } |
  { 'Err' : ApiError };
export type StatusCode = number;
export interface StatusCodeRecord { 'status_code' : StatusCode }
export type StatusCodeRecordResult = { 'Ok' : StatusCodeRecord } |
  { 'Err' : ApiError };
export interface SystemMetrics {
  'total_cycles' : [] | [TotalCycles],
  'funnai_index' : number,
  'daily_burn_rate' : DailyBurnRate,
}
export type TextResult = { 'Ok' : string } |
  { 'Err' : ApiError };
export type TimeInterval = { 'Daily' : null };
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
export interface TotalBurnedRecord {
  'lastScanTimestampNs' : bigint,
  'lastScannedBlock' : bigint,
  'totalBurnedE8s' : bigint,
}
export type TotalBurnedResult = { 'Ok' : TotalBurnedRecord } |
  { 'Err' : ApiError };
export interface TotalCycles {
  'all' : CycleAmount,
  'protocol' : CycleAmount,
  'mainers' : CycleAmount,
}
export interface UpdateDailyMetricAdminInput {
  'date' : string,
  'input' : DailyMetricUpdateInput,
}
export interface http_header { 'value' : string, 'name' : string }
export interface http_request_result {
  'status' : bigint,
  'body' : Uint8Array | number[],
  'headers' : Array<http_header>,
}
export interface _SERVICE extends ApiCanister {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
