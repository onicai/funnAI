export const idlFactory = ({ IDL }) => {
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
  const ChallengeResponseSubmissionInput = IDL.Record({
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
    'submittedBy' : IDL.Principal,
    'mainerTemp' : IDL.Float64,
    'challengeStatus' : ChallengeStatus,
    'cyclesGenerateResponseOwnctrlGs' : IDL.Nat,
    'challengeQuestionSeed' : IDL.Nat32,
    'mainerNumTokens' : IDL.Nat64,
    'challengeQuestion' : IDL.Text,
    'challengeId' : IDL.Text,
    'challengeQueuedBy' : IDL.Principal,
    'challengeQueuedId' : IDL.Text,
    'challengeQueuedTo' : IDL.Principal,
    'challengeTopic' : IDL.Text,
    'cyclesGenerateChallengeChctrlChllm' : IDL.Nat,
    'cyclesGenerateResponseSactrlSsctrl' : IDL.Nat,
    'judgePromptId' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'challengeAnswer' : IDL.Text,
    'challengeQueuedTimestamp' : IDL.Nat64,
    'cyclesSubmitResponse' : IDL.Nat,
    'cyclesGenerateChallengeGsChctrl' : IDL.Nat,
    'cyclesGenerateResponseSsctrlGs' : IDL.Nat,
  });
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
  const ChallengeQueueInput = IDL.Record({
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
    'challengeQueuedBy' : IDL.Principal,
    'challengeQueuedId' : IDL.Text,
    'challengeQueuedTo' : IDL.Principal,
    'challengeTopic' : IDL.Text,
    'cyclesGenerateChallengeChctrlChllm' : IDL.Nat,
    'cyclesGenerateResponseSactrlSsctrl' : IDL.Nat,
    'judgePromptId' : IDL.Text,
    'challengeQueuedTimestamp' : IDL.Nat64,
    'cyclesSubmitResponse' : IDL.Nat,
    'cyclesGenerateChallengeGsChctrl' : IDL.Nat,
    'cyclesGenerateResponseSsctrlGs' : IDL.Nat,
  });
  const ChallengeQueueInputResult = IDL.Variant({
    'Ok' : ChallengeQueueInput,
    'Err' : ApiError,
  });
  const AddCyclesRecord = IDL.Record({
    'added' : IDL.Bool,
    'amount' : IDL.Nat,
  });
  const AddCyclesResult = IDL.Variant({
    'Ok' : AddCyclesRecord,
    'Err' : ApiError,
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
  const MainerAgentCanisterResult = IDL.Variant({
    'Ok' : OfficialMainerAgentCanister,
    'Err' : ApiError,
  });
  const CanisterIDRecord = IDL.Record({ 'canister_id' : IDL.Text });
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
  const AdminRoleAssignmentsResult = IDL.Variant({
    'Ok' : IDL.Vec(AdminRoleAssignment),
    'Err' : ApiError,
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
  const MainerAgentSettings = IDL.Record({
    'creationTimestamp' : IDL.Nat64,
    'createdBy' : IDL.Principal,
    'cyclesBurnRate' : CyclesBurnRateDefault,
  });
  const MainerAgentSettingsListResult = IDL.Variant({
    'Ok' : IDL.Vec(MainerAgentSettings),
    'Err' : ApiError,
  });
  const MainerAgentTimers = IDL.Record({
    'recurringTimerId1' : IDL.Opt(IDL.Nat),
    'recurringTimerId2' : IDL.Opt(IDL.Nat),
    'randomInitialTimer1InSeconds' : IDL.Opt(IDL.Nat),
    'creationTimestamp' : IDL.Nat64,
    'calledFromEndpoint' : IDL.Text,
    'createdBy' : IDL.Principal,
    'action2RegularityInSeconds' : IDL.Nat,
    'initialTimerId1' : IDL.Opt(IDL.Nat),
    'action1RegularityInSeconds' : IDL.Nat,
  });
  const MainerAgentTimersListResult = IDL.Variant({
    'Ok' : IDL.Vec(MainerAgentTimers),
    'Err' : ApiError,
  });
  const ChallengeQueueInputsResult = IDL.Variant({
    'Ok' : IDL.Vec(ChallengeQueueInput),
    'Err' : ApiError,
  });
  const MainerAgentSettingsResult = IDL.Variant({
    'Ok' : MainerAgentSettings,
    'Err' : ApiError,
  });
  const MainerAgentTimersResult = IDL.Variant({
    'Ok' : MainerAgentTimers,
    'Err' : ApiError,
  });
  const IssueFlagsRecord = IDL.Record({ 'lowCycleBalance' : IDL.Bool });
  const IssueFlagsRetrievalResult = IDL.Variant({
    'Ok' : IssueFlagsRecord,
    'Err' : ApiError,
  });
  const CanisterAddressesResult = IDL.Variant({
    'Ok' : IDL.Vec(CanisterAddress),
    'Err' : ApiError,
  });
  const MainerAgentCanisterTypeResult = IDL.Variant({
    'Ok' : MainerAgentCanisterType,
    'Err' : ApiError,
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
  const FlagRecord = IDL.Record({ 'flag' : IDL.Bool });
  const FlagResult = IDL.Variant({ 'Ok' : FlagRecord, 'Err' : ApiError });
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
    'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : IDL.Nat,
    'protocolOperationFeesCut' : IDL.Nat,
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeCreationTimestamp' : IDL.Nat64,
    'challengeCreatedBy' : CanisterAddress,
    'challengeTopicId' : IDL.Text,
    'cyclesGenerateResponseOwnctrlOwnllmHIGH' : IDL.Nat,
    'submittedTimestamp' : IDL.Nat64,
    'cyclesGenerateResponseOwnctrlOwnllmLOW' : IDL.Nat,
    'mainerPromptId' : IDL.Text,
    'cyclesGenerateResponseSsctrlSsllm' : IDL.Nat,
    'mainerMaxContinueLoopCount' : IDL.Nat,
    'submittedBy' : IDL.Principal,
    'mainerTemp' : IDL.Float64,
    'challengeStatus' : ChallengeStatus,
    'cyclesGenerateResponseOwnctrlGs' : IDL.Nat,
    'challengeQuestionSeed' : IDL.Nat32,
    'mainerNumTokens' : IDL.Nat64,
    'submissionStatus' : ChallengeResponseSubmissionStatus,
    'challengeQuestion' : IDL.Text,
    'challengeId' : IDL.Text,
    'challengeQueuedBy' : IDL.Principal,
    'challengeQueuedId' : IDL.Text,
    'challengeQueuedTo' : IDL.Principal,
    'challengeTopic' : IDL.Text,
    'cyclesGenerateChallengeChctrlChllm' : IDL.Nat,
    'cyclesGenerateScoreGsJuctrl' : IDL.Nat,
    'cyclesGenerateResponseSactrlSsctrl' : IDL.Nat,
    'judgePromptId' : IDL.Text,
    'submissionId' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'challengeAnswer' : IDL.Text,
    'challengeQueuedTimestamp' : IDL.Nat64,
    'cyclesSubmitResponse' : IDL.Nat,
    'cyclesGenerateChallengeGsChctrl' : IDL.Nat,
    'cyclesGenerateScoreJuctrlJullm' : IDL.Nat,
    'cyclesGenerateResponseSsctrlGs' : IDL.Nat,
  });
  const ChallengeResponseSubmissionsResult = IDL.Variant({
    'Ok' : IDL.Vec(ChallengeResponseSubmission),
    'Err' : ApiError,
  });
  const CanisterIDRecordResult = IDL.Variant({
    'Ok' : CanisterIDRecord,
    'Err' : ApiError,
  });
  const MainerTimers = IDL.Record({
    'action2RegularityInSeconds' : IDL.Nat,
    'action1RegularityInSeconds' : IDL.Nat,
  });
  const MainerTimersResult = IDL.Variant({
    'Ok' : MainerTimers,
    'Err' : ApiError,
  });
  const NatResult = IDL.Variant({ 'Ok' : IDL.Nat, 'Err' : ApiError });
  const MainerTimerBuffers = IDL.Record({
    'bufferTimerId1' : IDL.Vec(IDL.Nat),
    'bufferTimerId2' : IDL.Vec(IDL.Nat),
  });
  const MainerTimerBuffersResult = IDL.Variant({
    'Ok' : MainerTimerBuffers,
    'Err' : ApiError,
  });
  const LlmCanistersRecord = IDL.Record({
    'roundRobinUseAll' : IDL.Bool,
    'roundRobinLLMs' : IDL.Nat,
    'llmCanisterIds' : IDL.Vec(CanisterAddress),
  });
  const LlmCanistersRecordResult = IDL.Variant({
    'Ok' : LlmCanistersRecord,
    'Err' : ApiError,
  });
  const TextResult = IDL.Variant({ 'Ok' : IDL.Text, 'Err' : ApiError });
  const AuthRecord = IDL.Record({ 'auth' : IDL.Text });
  const AuthRecordResult = IDL.Variant({ 'Ok' : AuthRecord, 'Err' : ApiError });
  const MainerAgentSettingsInput = IDL.Record({
    'cyclesBurnRate' : CyclesBurnRateDefault,
  });
  const MainerAgentCtrlbCanister = IDL.Service({
    'addChallengeResponseToShareAgent' : IDL.Func(
        [ChallengeResponseSubmissionInput],
        [StatusCodeRecordResult],
        [],
      ),
    'addChallengeToShareServiceQueue' : IDL.Func(
        [ChallengeQueueInput],
        [ChallengeQueueInputResult],
        [],
      ),
    'addCycles' : IDL.Func([], [AddCyclesResult], []),
    'addMainerShareAgentCanister' : IDL.Func(
        [OfficialMainerAgentCanister],
        [MainerAgentCanisterResult],
        [],
      ),
    'addMainerShareAgentCanisterAdmin' : IDL.Func(
        [OfficialMainerAgentCanister],
        [MainerAgentCanisterResult],
        [],
      ),
    'add_llm_canister' : IDL.Func(
        [CanisterIDRecord],
        [StatusCodeRecordResult],
        [],
      ),
    'amiController' : IDL.Func([], [StatusCodeRecordResult], ['query']),
    'assignAdminRole' : IDL.Func(
        [AssignAdminRoleInputRecord],
        [AdminRoleAssignmentResult],
        [],
      ),
    'canAgentSettingsBeUpdated' : IDL.Func([], [StatusCodeRecordResult], []),
    'checkAccessToLLMs' : IDL.Func([], [StatusCodeRecordResult], []),
    'getAdminRoles' : IDL.Func([], [AdminRoleAssignmentsResult], ['query']),
    'getAgentSettingsAdmin' : IDL.Func(
        [],
        [MainerAgentSettingsListResult],
        ['query'],
      ),
    'getAgentTimersAdmin' : IDL.Func(
        [],
        [MainerAgentTimersListResult],
        ['query'],
      ),
    'getChallengeQueueAdmin' : IDL.Func(
        [],
        [ChallengeQueueInputsResult],
        ['query'],
      ),
    'getCurrentAgentSettingsAdmin' : IDL.Func(
        [],
        [MainerAgentSettingsResult],
        ['query'],
      ),
    'getCurrentAgentTimersAdmin' : IDL.Func(
        [],
        [MainerAgentTimersResult],
        ['query'],
      ),
    'getGameStateCanisterId' : IDL.Func([], [IDL.Text], ['query']),
    'getIssueFlagsAdmin' : IDL.Func([], [IssueFlagsRetrievalResult], ['query']),
    'getLLMCanisterIds' : IDL.Func([], [CanisterAddressesResult], ['query']),
    'getMainerCanisterType' : IDL.Func(
        [],
        [MainerAgentCanisterTypeResult],
        ['query'],
      ),
    'getMainerStatisticsAdmin' : IDL.Func(
        [],
        [StatisticsRetrievalResult],
        ['query'],
      ),
    'getMaintenanceFlag' : IDL.Func([], [FlagResult], ['query']),
    'getRecentSubmittedResponsesAdmin' : IDL.Func(
        [],
        [ChallengeResponseSubmissionsResult],
        ['query'],
      ),
    'getRoundRobinCanister' : IDL.Func([], [CanisterIDRecordResult], ['query']),
    'getShareServiceCanisterId' : IDL.Func([], [IDL.Text], ['query']),
    'getSubmittedResponsesAdmin' : IDL.Func(
        [],
        [ChallengeResponseSubmissionsResult],
        ['query'],
      ),
    'getTimerActionRegularityInSecondsAdmin' : IDL.Func(
        [],
        [MainerTimersResult],
        ['query'],
      ),
    'getTimerBufferMaxSizeAdmin' : IDL.Func([], [NatResult], ['query']),
    'getTimerBuffersAdmin' : IDL.Func(
        [],
        [MainerTimerBuffersResult],
        ['query'],
      ),
    'get_llm_canisters' : IDL.Func([], [LlmCanistersRecordResult], ['query']),
    'health' : IDL.Func([], [StatusCodeRecordResult], ['query']),
    'ready' : IDL.Func([], [StatusCodeRecordResult], []),
    'remove_llm_canister' : IDL.Func(
        [CanisterIDRecord],
        [StatusCodeRecordResult],
        [],
      ),
    'resetChallengeQueueAdmin' : IDL.Func([], [StatusCodeRecordResult], []),
    'resetRoundRobinLLMs' : IDL.Func([], [StatusCodeRecordResult], []),
    'reset_llm_canisters' : IDL.Func([], [StatusCodeRecordResult], []),
    'revokeAdminRole' : IDL.Func([IDL.Text], [TextResult], []),
    'setGameStateCanisterId' : IDL.Func(
        [IDL.Text],
        [StatusCodeRecordResult],
        [],
      ),
    'setMainerCanisterType' : IDL.Func(
        [MainerAgentCanisterType],
        [StatusCodeRecordResult],
        [],
      ),
    'setRoundRobinLLMs' : IDL.Func([IDL.Nat], [StatusCodeRecordResult], []),
    'setShareServiceCanisterId' : IDL.Func(
        [IDL.Text],
        [StatusCodeRecordResult],
        [],
      ),
    'setTimerAction2RegularityInSecondsAdmin' : IDL.Func(
        [IDL.Nat],
        [StatusCodeRecordResult],
        [],
      ),
    'setTimerBufferMaxSizeAdmin' : IDL.Func(
        [IDL.Nat],
        [StatusCodeRecordResult],
        [],
      ),
    'startTimerExecutionAdmin' : IDL.Func([], [AuthRecordResult], []),
    'stopTimerExecutionAdmin' : IDL.Func([], [AuthRecordResult], []),
    'timeToNextAgentSettingsUpdate' : IDL.Func([], [NatResult], []),
    'toggleMaintenanceFlagAdmin' : IDL.Func([], [AuthRecordResult], []),
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
