export const idlFactory = ({ IDL }) => {
  const CanisterIDRecord = IDL.Record({ 'canister_id' : IDL.Text });
  const StatusCode = IDL.Nat16;
  const StatusCodeRecord = IDL.Record({ 'status_code' : StatusCode });
  const ApiError = IDL.Variant({
    'FailedOperation' : IDL.Null,
    'InvalidId' : IDL.Null,
    'ZeroAddress' : IDL.Null,
    'Unauthorized' : IDL.Null,
    'StatusCode' : StatusCode,
    'Other' : IDL.Text,
    'InsuffientCycles' : IDL.Nat,
  });
  const StatusCodeRecordResult = IDL.Variant({
    'Ok' : StatusCodeRecord,
    'Err' : ApiError,
  });
  const IssueFlagsRecord = IDL.Record({ 'lowCycleBalance' : IDL.Bool });
  const IssueFlagsRetrievalResult = IDL.Variant({
    'Ok' : IssueFlagsRecord,
    'Err' : ApiError,
  });
  const TimeInterval = IDL.Variant({ 'Daily' : IDL.Null });
  const CyclesBurnRate = IDL.Record({
    'cycles' : IDL.Nat,
    'timeInterval' : TimeInterval,
  });
  const StatisticsRecord = IDL.Record({
    'cycleBalance' : IDL.Nat,
    'totalCyclesBurnt' : IDL.Nat,
    'cyclesBurnRate' : CyclesBurnRate,
  });
  const StatisticsRetrievalResult = IDL.Variant({
    'Ok' : StatisticsRecord,
    'Err' : ApiError,
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
  const ChallengeResponseSubmissionStatus = IDL.Variant({
    'Judged' : IDL.Null,
    'FailedSubmission' : IDL.Null,
    'Processed' : IDL.Null,
    'Judging' : IDL.Null,
    'Received' : IDL.Null,
    'Other' : IDL.Text,
    'Submitted' : IDL.Null,
  });
  const ChallengeResponseSubmission = IDL.Record({
    'challengeClosedTimestamp' : IDL.Opt(IDL.Nat64),
    'challengeTopicStatus' : ChallengeTopicStatus,
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeCreationTimestamp' : IDL.Nat64,
    'challengeCreatedBy' : CanisterAddress,
    'challengeTopicId' : IDL.Text,
    'submittedTimestamp' : IDL.Nat64,
    'submittedBy' : IDL.Principal,
    'challengeStatus' : ChallengeStatus,
    'challengeQuestionSeed' : IDL.Nat32,
    'submissionStatus' : ChallengeResponseSubmissionStatus,
    'challengeQuestion' : IDL.Text,
    'challengeId' : IDL.Text,
    'challengeTopic' : IDL.Text,
    'submissionId' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'submissionCyclesRequired' : IDL.Nat,
    'challengeAnswer' : IDL.Text,
  });
  const ChallengeResponseSubmissionsResult = IDL.Variant({
    'Ok' : IDL.Vec(ChallengeResponseSubmission),
    'Err' : ApiError,
  });
  const CanisterIDRecordResult = IDL.Variant({
    'Ok' : CanisterIDRecord,
    'Err' : ApiError,
  });
  const AuthRecord = IDL.Record({ 'auth' : IDL.Text });
  const AuthRecordResult = IDL.Variant({ 'Ok' : AuthRecord, 'Err' : ApiError });
  const MainerAgentSettingsInput = IDL.Record({
    'cyclesBurnRate' : CyclesBurnRate,
  });
  const MainerAgentCtrlbCanister = IDL.Service({
    'add_llm_canister' : IDL.Func(
        [CanisterIDRecord],
        [StatusCodeRecordResult],
        [],
      ),
    'amiController' : IDL.Func([], [StatusCodeRecordResult], ['query']),
    'checkAccessToLLMs' : IDL.Func([], [StatusCodeRecordResult], []),
    'getGameStateCanisterId' : IDL.Func([], [IDL.Text], ['query']),
    'getIssueFlagsAdmin' : IDL.Func([], [IssueFlagsRetrievalResult], ['query']),
    'getMainerStatisticsAdmin' : IDL.Func(
        [],
        [StatisticsRetrievalResult],
        ['query'],
      ),
    'getRecentSubmittedResponsesAdmin' : IDL.Func(
        [],
        [ChallengeResponseSubmissionsResult],
        ['query'],
      ),
    'getRoundRobinCanister' : IDL.Func([], [CanisterIDRecordResult], ['query']),
    'getSubmittedResponsesAdmin' : IDL.Func(
        [],
        [ChallengeResponseSubmissionsResult],
        ['query'],
      ),
    'health' : IDL.Func([], [StatusCodeRecordResult], ['query']),
    'ready' : IDL.Func([], [StatusCodeRecordResult], []),
    'reset_llm_canisters' : IDL.Func([], [StatusCodeRecordResult], []),
    'setGameStateCanisterId' : IDL.Func(
        [IDL.Text],
        [StatusCodeRecordResult],
        [],
      ),
    'setRoundRobinLLMs' : IDL.Func([IDL.Nat], [StatusCodeRecordResult], []),
    'startTimerExecutionAdmin' : IDL.Func([], [AuthRecordResult], []),
    'stopTimerExecutionAdmin' : IDL.Func([], [AuthRecordResult], []),
    'triggerChallengeResponseAdmin' : IDL.Func([], [AuthRecordResult], []),
    'updateAgentSettings' : IDL.Func(
        [MainerAgentSettingsInput],
        [StatusCodeRecordResult],
        [],
      ),
    'whoami' : IDL.Func([], [IDL.Principal], ['query']),
  });
  return MainerAgentCtrlbCanister;
};
export const init = ({ IDL }) => { return []; };
