export const idlFactory = ({ IDL }) => {
  const AuthRecord = IDL.Record({ 'auth' : IDL.Text });
  const StatusCode = IDL.Nat16;
  const ApiError = IDL.Variant({
    'FailedOperation' : IDL.Null,
    'InvalidId' : IDL.Null,
    'ZeroAddress' : IDL.Null,
    'Unauthorized' : IDL.Null,
    'StatusCode' : StatusCode,
    'Other' : IDL.Text,
    'InsuffientCycles' : IDL.Nat,
  });
  const AuthRecordResult = IDL.Variant({ 'Ok' : AuthRecord, 'Err' : ApiError });
  const AdminRole = IDL.Variant({
    'AdminQuery' : IDL.Null,
    'AdminUpdate' : IDL.Null,
  });
  const AssignAdminRoleInputRecord = IDL.Record({
    'principal' : IDL.Text,
    'note' : IDL.Text,
    'role' : AdminRole,
  });
  const AdminRoleAssignment = IDL.Record({
    'principal' : IDL.Text,
    'assignedAt' : IDL.Nat64,
    'assignedBy' : IDL.Text,
    'note' : IDL.Text,
    'role' : AdminRole,
  });
  const AdminRoleAssignmentResult = IDL.Variant({
    'Ok' : AdminRoleAssignment,
    'Err' : ApiError,
  });
  const DailyMetricInput = IDL.Record({
    'total_paused_mainers' : IDL.Nat,
    'total_cycles_all_usd' : IDL.Opt(IDL.Float64),
    'total_cycles_protocol' : IDL.Opt(IDL.Nat),
    'total_cycles_mainers_usd' : IDL.Opt(IDL.Float64),
    'date' : IDL.Text,
    'paused_very_high_burn_rate_mainers' : IDL.Nat,
    'paused_medium_burn_rate_mainers' : IDL.Nat,
    'total_cycles_all_mainers' : IDL.Nat,
    'paused_custom_burn_rate_mainers' : IDL.Nat,
    'active_very_high_burn_rate_mainers' : IDL.Nat,
    'active_high_burn_rate_mainers' : IDL.Nat,
    'active_low_burn_rate_mainers' : IDL.Nat,
    'paused_low_burn_rate_mainers' : IDL.Nat,
    'daily_burn_rate_usd' : IDL.Float64,
    'paused_high_burn_rate_mainers' : IDL.Nat,
    'total_active_mainers' : IDL.Nat,
    'total_cycles_all' : IDL.Opt(IDL.Nat),
    'active_medium_burn_rate_mainers' : IDL.Nat,
    'active_custom_burn_rate_mainers' : IDL.Nat,
    'daily_burn_rate_cycles' : IDL.Nat,
    'funnai_index' : IDL.Float64,
    'total_mainers_created' : IDL.Nat,
    'total_cycles_protocol_usd' : IDL.Opt(IDL.Float64),
  });
  const NatResult = IDL.Variant({ 'Ok' : IDL.Nat, 'Err' : ApiError });
  const DerivedMetrics = IDL.Record({
    'avg_cycles_per_mainer' : IDL.Float64,
    'paused_percentage' : IDL.Float64,
    'tier_distribution' : IDL.Record({
      'low' : IDL.Float64,
      'custom' : IDL.Float64,
      'high' : IDL.Float64,
      'very_high' : IDL.Float64,
      'medium' : IDL.Float64,
    }),
    'burn_rate_per_active_mainer' : IDL.Float64,
    'active_percentage' : IDL.Float64,
  });
  const MainersTierBreakdown = IDL.Record({
    'low' : IDL.Nat,
    'custom' : IDL.Nat,
    'high' : IDL.Nat,
    'very_high' : IDL.Nat,
    'medium' : IDL.Nat,
  });
  const MainersMetrics = IDL.Record({
    'totals' : IDL.Record({
      'created' : IDL.Nat,
      'active' : IDL.Nat,
      'total_cycles' : IDL.Nat,
      'paused' : IDL.Nat,
    }),
    'breakdown_by_tier' : IDL.Record({
      'active' : MainersTierBreakdown,
      'paused' : MainersTierBreakdown,
    }),
  });
  const DailyMetricMetadata = IDL.Record({
    'updated_at' : IDL.Text,
    'date' : IDL.Text,
    'created_at' : IDL.Text,
  });
  const CycleAmount = IDL.Record({ 'usd' : IDL.Float64, 'cycles' : IDL.Nat });
  const TotalCycles = IDL.Record({
    'all' : CycleAmount,
    'protocol' : CycleAmount,
    'mainers' : CycleAmount,
  });
  const DailyBurnRate = IDL.Record({ 'usd' : IDL.Float64, 'cycles' : IDL.Nat });
  const SystemMetrics = IDL.Record({
    'total_cycles' : IDL.Opt(TotalCycles),
    'funnai_index' : IDL.Float64,
    'daily_burn_rate' : DailyBurnRate,
  });
  const DailyMetric = IDL.Record({
    'derived_metrics' : DerivedMetrics,
    'mainers' : MainersMetrics,
    'metadata' : DailyMetricMetadata,
    'system_metrics' : SystemMetrics,
  });
  const DailyMetricResult = IDL.Variant({
    'Ok' : DailyMetric,
    'Err' : ApiError,
  });
  const ActivityFeedQuery = IDL.Record({
    'challengesLimit' : IDL.Opt(IDL.Nat),
    'sinceTimestamp' : IDL.Opt(IDL.Nat64),
    'winnersOffset' : IDL.Opt(IDL.Nat),
    'challengesOffset' : IDL.Opt(IDL.Nat),
    'winnersLimit' : IDL.Opt(IDL.Nat),
  });
  const ChallengeTopicStatus = IDL.Variant({
    'Open' : IDL.Null,
    'Closed' : IDL.Null,
    'Archived' : IDL.Null,
    'Other' : IDL.Text,
  });
  const CanisterAddress = IDL.Text;
  const ChallengeStatus = IDL.Variant({
    'Open' : IDL.Null,
    'Closed' : IDL.Null,
    'Archived' : IDL.Null,
    'Other' : IDL.Text,
  });
  const Challenge = IDL.Record({
    'challengeClosedTimestamp' : IDL.Opt(IDL.Nat64),
    'challengeTopicStatus' : ChallengeTopicStatus,
    'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : IDL.Nat,
    'protocolOperationFeesCut' : IDL.Nat,
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeCreationTimestamp' : IDL.Nat64,
    'challengeCreatedBy' : CanisterAddress,
    'challengeTopicId' : IDL.Text,
    'cyclesGenerateResponseOwnctrlOwnllmHIGH' : IDL.Nat,
    'cyclesGenerateResponseOwnctrlOwnllmLOW' : IDL.Nat,
    'mainerPromptId' : IDL.Text,
    'cyclesGenerateResponseSsctrlSsllm' : IDL.Nat,
    'mainerMaxContinueLoopCount' : IDL.Nat,
    'mainerTemp' : IDL.Float64,
    'challengeStatus' : ChallengeStatus,
    'cyclesGenerateResponseOwnctrlGs' : IDL.Nat,
    'challengeQuestionSeed' : IDL.Nat32,
    'mainerNumTokens' : IDL.Nat64,
    'challengeQuestion' : IDL.Text,
    'challengeId' : IDL.Text,
    'challengeTopic' : IDL.Text,
    'cyclesGenerateChallengeChctrlChllm' : IDL.Nat,
    'cyclesGenerateResponseSactrlSsctrl' : IDL.Nat,
    'judgePromptId' : IDL.Text,
    'cyclesSubmitResponse' : IDL.Nat,
    'cyclesGenerateChallengeGsChctrl' : IDL.Nat,
    'cyclesGenerateResponseSsctrlGs' : IDL.Nat,
  });
  const ChallengeParticipationResult = IDL.Variant({
    'ThirdPlace' : IDL.Null,
    'SecondPlace' : IDL.Null,
    'Winner' : IDL.Null,
    'Other' : IDL.Text,
    'Participated' : IDL.Null,
  });
  const RewardType = IDL.Variant({
    'ICP' : IDL.Null,
    'Coupon' : IDL.Text,
    'MainerToken' : IDL.Null,
    'Cycles' : IDL.Null,
    'Other' : IDL.Text,
  });
  const ChallengeWinnerReward = IDL.Record({
    'distributed' : IDL.Bool,
    'rewardDetails' : IDL.Text,
    'rewardType' : RewardType,
    'amount' : IDL.Nat,
    'distributedTimestamp' : IDL.Opt(IDL.Nat64),
  });
  const ChallengeParticipantEntry = IDL.Record({
    'result' : ChallengeParticipationResult,
    'reward' : ChallengeWinnerReward,
    'ownedBy' : IDL.Principal,
    'submittedBy' : IDL.Principal,
    'submissionId' : IDL.Text,
  });
  const ChallengeWinnerDeclarationArray = IDL.Record({
    'participants' : IDL.Vec(ChallengeParticipantEntry),
    'thirdPlace' : ChallengeParticipantEntry,
    'winner' : ChallengeParticipantEntry,
    'secondPlace' : ChallengeParticipantEntry,
    'finalizedTimestamp' : IDL.Nat64,
    'challengeId' : IDL.Text,
  });
  const ActivityFeedResponse = IDL.Record({
    'totalWinners' : IDL.Nat,
    'cacheTimestamp' : IDL.Nat64,
    'totalChallenges' : IDL.Nat,
    'challenges' : IDL.Vec(Challenge),
    'winners' : IDL.Vec(ChallengeWinnerDeclarationArray),
  });
  const ActivityFeedResult = IDL.Variant({
    'Ok' : ActivityFeedResponse,
    'Err' : ApiError,
  });
  const CacheStatus = IDL.Record({
    'syncIntervalSeconds' : IDL.Nat,
    'cachedChallengesCount' : IDL.Nat,
    'lastSyncTimestamp' : IDL.Nat64,
    'cachedWinnersCount' : IDL.Nat,
  });
  const CacheStatusResult = IDL.Variant({
    'Ok' : CacheStatus,
    'Err' : ApiError,
  });
  const AdminRoleAssignmentsResult = IDL.Variant({
    'Ok' : IDL.Vec(AdminRoleAssignment),
    'Err' : ApiError,
  });
  const DailyMetricsQuery = IDL.Record({
    'end_date' : IDL.Opt(IDL.Text),
    'limit' : IDL.Opt(IDL.Nat),
    'start_date' : IDL.Opt(IDL.Text),
  });
  const PeriodInfo = IDL.Record({
    'end_date' : IDL.Text,
    'total_days' : IDL.Nat,
    'start_date' : IDL.Text,
  });
  const DailyMetricsResponse = IDL.Record({
    'period' : PeriodInfo,
    'daily_metrics' : IDL.Vec(DailyMetric),
  });
  const DailyMetricsResult = IDL.Variant({
    'Ok' : DailyMetricsResponse,
    'Err' : ApiError,
  });
  const DailyMetricsRunStatus = IDL.Record({
    'lastFailureMessage' : IDL.Opt(IDL.Text),
    'timerActive' : IDL.Bool,
    'lastSuccessfulMetricDate' : IDL.Opt(IDL.Text),
  });
  const Result = IDL.Variant({
    'Ok' : DailyMetricsRunStatus,
    'Err' : ApiError,
  });
  const ChallengesResult = IDL.Variant({
    'Ok' : IDL.Vec(Challenge),
    'Err' : ApiError,
  });
  const PricingCache = IDL.Record({
    'xdrPermyriadPerIcp' : IDL.Nat64,
    'lastUpdatedNs' : IDL.Nat64,
    'icApiTcycleBurnRatePerDay' : IDL.Float64,
    'usdPerComputedXdr' : IDL.Float64,
  });
  const PricingCacheResult = IDL.Variant({
    'Ok' : PricingCache,
    'Err' : ApiError,
  });
  const TokenRewardsMetadata = IDL.Record({
    'dataset' : IDL.Text,
    'description' : IDL.Text,
    'last_updated' : IDL.Text,
    'version' : IDL.Text,
    'units' : IDL.Record({
      'rewards_per_challenge' : IDL.Text,
      'total_minted' : IDL.Text,
    }),
  });
  const TokenRewardsEntry = IDL.Record({
    'date' : IDL.Text,
    'quarter' : IDL.Text,
    'rewards_per_challenge' : IDL.Float64,
    'total_minted' : IDL.Float64,
    'notes' : IDL.Text,
    'rewards_per_quarter' : IDL.Float64,
  });
  const TokenRewardsData = IDL.Record({
    'metadata' : TokenRewardsMetadata,
    'data' : IDL.Vec(TokenRewardsEntry),
  });
  const TokenRewardsDataResult = IDL.Variant({
    'Ok' : TokenRewardsData,
    'Err' : ApiError,
  });
  const TotalBurnedRecord = IDL.Record({
    'lastScanTimestampNs' : IDL.Nat64,
    'lastScannedBlock' : IDL.Nat,
    'totalBurnedE8s' : IDL.Nat,
  });
  const TotalBurnedResult = IDL.Variant({
    'Ok' : TotalBurnedRecord,
    'Err' : ApiError,
  });
  const StatusCodeRecord = IDL.Record({ 'status_code' : StatusCode });
  const StatusCodeRecordResult = IDL.Variant({
    'Ok' : StatusCodeRecord,
    'Err' : ApiError,
  });
  const TextResult = IDL.Variant({ 'Ok' : IDL.Text, 'Err' : ApiError });
  const http_header = IDL.Record({ 'value' : IDL.Text, 'name' : IDL.Text });
  const http_request_result = IDL.Record({
    'status' : IDL.Nat,
    'body' : IDL.Vec(IDL.Nat8),
    'headers' : IDL.Vec(http_header),
  });
  const LlmSetupStatus = IDL.Variant({
    'CodeInstallInProgress' : IDL.Null,
    'CanisterCreated' : IDL.Null,
    'ConfigurationInProgress' : IDL.Null,
    'CanisterCreationInProgress' : IDL.Null,
    'ModelUploadProgress' : IDL.Nat8,
  });
  const CanisterStatus = IDL.Variant({
    'Paused' : IDL.Null,
    'Paid' : IDL.Null,
    'Unlocked' : IDL.Null,
    'LlmSetupFinished' : IDL.Null,
    'ControllerCreated' : IDL.Null,
    'LlmSetupInProgress' : LlmSetupStatus,
    'Running' : IDL.Null,
    'Other' : IDL.Text,
    'ControllerCreationInProgress' : IDL.Null,
  });
  const MainerAgentCanisterType = IDL.Variant({
    'NA' : IDL.Null,
    'Own' : IDL.Null,
    'ShareAgent' : IDL.Null,
    'ShareService' : IDL.Null,
  });
  const ProtocolCanisterType = IDL.Variant({
    'MainerAgent' : MainerAgentCanisterType,
    'MainerLlm' : IDL.Null,
    'Challenger' : IDL.Null,
    'Judge' : IDL.Null,
    'Verifier' : IDL.Null,
    'MainerCreator' : IDL.Null,
  });
  const SelectableMainerLLMs = IDL.Variant({ 'Qwen2_5_500M' : IDL.Null });
  const MainerConfigurationInput = IDL.Record({
    'selectedLLM' : IDL.Opt(SelectableMainerLLMs),
    'subnetLlm' : IDL.Text,
    'mainerAgentCanisterType' : MainerAgentCanisterType,
    'cyclesForMainer' : IDL.Nat,
    'subnetCtrl' : IDL.Text,
  });
  const OfficialMainerAgentCanister = IDL.Record({
    'status' : CanisterStatus,
    'canisterType' : ProtocolCanisterType,
    'ownedBy' : IDL.Principal,
    'creationTimestamp' : IDL.Nat64,
    'createdBy' : IDL.Principal,
    'mainerConfig' : MainerConfigurationInput,
    'subnet' : IDL.Text,
    'address' : CanisterAddress,
  });
  const TimeInterval = IDL.Variant({ 'Daily' : IDL.Null });
  const CyclesBurnRate = IDL.Record({
    'cycles' : IDL.Nat,
    'timeInterval' : TimeInterval,
  });
  const CyclesBurnRateDefault = IDL.Variant({
    'Low' : IDL.Null,
    'Mid' : IDL.Null,
    'VeryHigh' : IDL.Null,
    'High' : IDL.Null,
    'Custom' : CyclesBurnRate,
  });
  const ShareAgentActivity = IDL.Record({
    'cycleBalance' : IDL.Nat,
    'cyclesBurnRate' : CyclesBurnRateDefault,
    'address' : IDL.Text,
    'lastChallengeRequestTimestamp' : IDL.Nat64,
  });
  const ShareAgentRegistryWithActivity = IDL.Record({
    'registry' : IDL.Vec(OfficialMainerAgentCanister),
    'activity' : IDL.Vec(ShareAgentActivity),
  });
  const ShareAgentRegistryWithActivityResult = IDL.Variant({
    'Ok' : ShareAgentRegistryWithActivity,
    'Err' : ApiError,
  });
  const DailyMetricUpdateInput = IDL.Record({
    'total_paused_mainers' : IDL.Opt(IDL.Nat),
    'total_cycles_all_usd' : IDL.Opt(IDL.Float64),
    'total_cycles_protocol' : IDL.Opt(IDL.Nat),
    'total_cycles_mainers_usd' : IDL.Opt(IDL.Float64),
    'paused_very_high_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'paused_medium_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'total_cycles_all_mainers' : IDL.Opt(IDL.Nat),
    'paused_custom_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'active_very_high_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'active_high_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'active_low_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'paused_low_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'daily_burn_rate_usd' : IDL.Opt(IDL.Float64),
    'paused_high_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'total_active_mainers' : IDL.Opt(IDL.Nat),
    'total_cycles_all' : IDL.Opt(IDL.Nat),
    'active_medium_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'active_custom_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'daily_burn_rate_cycles' : IDL.Opt(IDL.Nat),
    'funnai_index' : IDL.Opt(IDL.Float64),
    'total_mainers_created' : IDL.Opt(IDL.Nat),
    'total_cycles_protocol_usd' : IDL.Opt(IDL.Float64),
  });
  const UpdateDailyMetricAdminInput = IDL.Record({
    'date' : IDL.Text,
    'input' : DailyMetricUpdateInput,
  });
  const ApiCanister = IDL.Service({
    'amiController' : IDL.Func([], [AuthRecordResult], ['query']),
    'assignAdminRole' : IDL.Func(
        [AssignAdminRoleInputRecord],
        [AdminRoleAssignmentResult],
        [],
      ),
    'bulkCreateDailyMetricsAdmin' : IDL.Func(
        [IDL.Vec(DailyMetricInput)],
        [NatResult],
        [],
      ),
    'createDailyMetricAdmin' : IDL.Func(
        [DailyMetricInput],
        [DailyMetricResult],
        [],
      ),
    'deleteDailyMetricAdmin' : IDL.Func([IDL.Text], [NatResult], []),
    'getActivityFeed' : IDL.Func(
        [ActivityFeedQuery],
        [ActivityFeedResult],
        ['query'],
      ),
    'getActivityFeedCacheStatus' : IDL.Func([], [CacheStatusResult], ['query']),
    'getActivityFeedSyncIntervalAdmin' : IDL.Func([], [NatResult], ['query']),
    'getAdminRoles' : IDL.Func([], [AdminRoleAssignmentsResult], ['query']),
    'getDailyMetricByDate' : IDL.Func(
        [IDL.Text],
        [DailyMetricResult],
        ['query'],
      ),
    'getDailyMetrics' : IDL.Func(
        [IDL.Opt(DailyMetricsQuery)],
        [DailyMetricsResult],
        ['query'],
      ),
    'getDailyMetricsAdmin' : IDL.Func([], [DailyMetricsResult], ['query']),
    'getDailyMetricsRunStatusAdmin' : IDL.Func([], [Result], ['query']),
    'getLatestDailyMetric' : IDL.Func([], [DailyMetricResult], ['query']),
    'getMasterCanisterId' : IDL.Func([], [AuthRecordResult], ['query']),
    'getNumDailyMetrics' : IDL.Func([], [NatResult], ['query']),
    'getOpenChallengesFromCache' : IDL.Func([], [ChallengesResult], ['query']),
    'getPricingCacheAdmin' : IDL.Func([], [PricingCacheResult], ['query']),
    'getShareServiceCanisterIdAdmin' : IDL.Func(
        [],
        [AuthRecordResult],
        ['query'],
      ),
    'getTokenIndexCanisterIdAdmin' : IDL.Func(
        [],
        [AuthRecordResult],
        ['query'],
      ),
    'getTokenRewardsData' : IDL.Func([], [TokenRewardsDataResult], ['query']),
    'getTotalBurned' : IDL.Func([], [TotalBurnedResult], ['query']),
    'health' : IDL.Func([], [StatusCodeRecordResult], ['query']),
    'previewDailyMetricsAggregationAdmin' : IDL.Func(
        [],
        [DailyMetricResult],
        [],
      ),
    'previewIsoDateAdmin' : IDL.Func([IDL.Int], [TextResult], ['query']),
    'pricingTransform' : IDL.Func(
        [
          IDL.Record({
            'context' : IDL.Vec(IDL.Nat8),
            'response' : http_request_result,
          }),
        ],
        [http_request_result],
        ['query'],
      ),
    'pullShareServiceSnapshotAdmin' : IDL.Func(
        [],
        [ShareAgentRegistryWithActivityResult],
        [],
      ),
    'resetDailyMetricsAdmin' : IDL.Func([], [NatResult], []),
    'revokeAdminRole' : IDL.Func([IDL.Text], [TextResult], []),
    'setActivityFeedSyncIntervalAdmin' : IDL.Func(
        [IDL.Nat],
        [StatusCodeRecordResult],
        [],
      ),
    'setMasterCanisterId' : IDL.Func([IDL.Text], [AuthRecordResult], []),
    'setShareServiceCanisterIdAdmin' : IDL.Func(
        [IDL.Text],
        [AuthRecordResult],
        [],
      ),
    'setTokenIndexCanisterIdAdmin' : IDL.Func(
        [IDL.Text],
        [AuthRecordResult],
        [],
      ),
    'startActivityFeedTimerAdmin' : IDL.Func([], [AuthRecordResult], []),
    'startBurnScanTimerAdmin' : IDL.Func([], [AuthRecordResult], []),
    'startDailyMetricsTimerAdmin' : IDL.Func([], [AuthRecordResult], []),
    'startPricingTimerAdmin' : IDL.Func([], [AuthRecordResult], []),
    'stopActivityFeedTimerAdmin' : IDL.Func([], [AuthRecordResult], []),
    'stopBurnScanTimerAdmin' : IDL.Func([], [AuthRecordResult], []),
    'stopDailyMetricsTimerAdmin' : IDL.Func([], [AuthRecordResult], []),
    'stopPricingTimerAdmin' : IDL.Func([], [AuthRecordResult], []),
    'triggerBurnScanAdmin' : IDL.Func([], [AuthRecordResult], []),
    'triggerDailyMetricsAggregationAdmin' : IDL.Func(
        [],
        [DailyMetricResult],
        [],
      ),
    'updateDailyMetricAdmin' : IDL.Func(
        [UpdateDailyMetricAdminInput],
        [DailyMetricResult],
        [],
      ),
    'whoami' : IDL.Func([], [IDL.Principal], ['query']),
  });
  return ApiCanister;
};
export const init = ({ IDL }) => { return []; };
