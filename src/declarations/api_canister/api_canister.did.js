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
    'active_medium_burn_rate_mainers' : IDL.Nat,
    'active_custom_burn_rate_mainers' : IDL.Nat,
    'daily_burn_rate_cycles' : IDL.Nat,
    'funnai_index' : IDL.Float64,
    'total_mainers_created' : IDL.Nat,
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
  const DailyBurnRate = IDL.Record({ 'usd' : IDL.Float64, 'cycles' : IDL.Nat });
  const SystemMetrics = IDL.Record({
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
  const StatusCodeRecord = IDL.Record({ 'status_code' : StatusCode });
  const StatusCodeRecordResult = IDL.Variant({
    'Ok' : StatusCodeRecord,
    'Err' : ApiError,
  });
  const TextResult = IDL.Variant({ 'Ok' : IDL.Text, 'Err' : ApiError });
  const DailyMetricUpdateInput = IDL.Record({
    'total_paused_mainers' : IDL.Opt(IDL.Nat),
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
    'active_medium_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'active_custom_burn_rate_mainers' : IDL.Opt(IDL.Nat),
    'daily_burn_rate_cycles' : IDL.Opt(IDL.Nat),
    'funnai_index' : IDL.Opt(IDL.Float64),
    'total_mainers_created' : IDL.Opt(IDL.Nat),
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
    'getLatestDailyMetric' : IDL.Func([], [DailyMetricResult], ['query']),
    'getMasterCanisterId' : IDL.Func([], [AuthRecordResult], ['query']),
    'getNumDailyMetrics' : IDL.Func([], [NatResult], ['query']),
    'getTokenRewardsData' : IDL.Func([], [TokenRewardsDataResult], ['query']),
    'health' : IDL.Func([], [StatusCodeRecordResult], ['query']),
    'resetDailyMetricsAdmin' : IDL.Func([], [NatResult], []),
    'revokeAdminRole' : IDL.Func([IDL.Text], [TextResult], []),
    'setMasterCanisterId' : IDL.Func([IDL.Text], [AuthRecordResult], []),
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
