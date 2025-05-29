export const idlFactory = ({ IDL }) => {
  const List = IDL.Rec();
  const List_1 = IDL.Rec();
  const ChallengeTopicStatus = IDL.Variant({
    'Open' : IDL.Null,
    'Closed' : IDL.Null,
    'Archived' : IDL.Null,
    'Other' : IDL.Text,
  });
  const NewChallengeInput = IDL.Record({
    'challengeTopicStatus' : ChallengeTopicStatus,
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeTopicId' : IDL.Text,
    'challengeQuestionSeed' : IDL.Nat32,
    'challengeQuestion' : IDL.Text,
    'challengeTopic' : IDL.Text,
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
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeCreationTimestamp' : IDL.Nat64,
    'challengeCreatedBy' : CanisterAddress,
    'challengeTopicId' : IDL.Text,
    'challengeStatus' : ChallengeStatus,
    'challengeQuestionSeed' : IDL.Nat32,
    'challengeQuestion' : IDL.Text,
    'challengeId' : IDL.Text,
    'challengeTopic' : IDL.Text,
    'submissionCyclesRequired' : IDL.Nat,
  });
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
  const ChallengeAdditionResult = IDL.Variant({
    'Ok' : Challenge,
    'Err' : ApiError,
  });
  const ChallengeTopicInput = IDL.Record({ 'challengeTopic' : IDL.Text });
  const ChallengeTopic = IDL.Record({
    'challengeTopicStatus' : ChallengeTopicStatus,
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeTopicId' : IDL.Text,
    'challengeTopic' : IDL.Text,
  });
  const ChallengeTopicResult = IDL.Variant({
    'Ok' : ChallengeTopic,
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
    'mainerAgentCanisterType' : MainerAgentCanisterType,
  });
  const OfficialMainerAgentCanister = IDL.Record({
    'status' : CanisterStatus,
    'canisterType' : ProtocolCanisterType,
    'ownedBy' : IDL.Principal,
    'creationTimestamp' : IDL.Nat64,
    'createdBy' : IDL.Principal,
    'mainerConfig' : MainerConfigurationInput,
    'address' : CanisterAddress,
  });
  const SetUpMainerLlmCanisterResult = IDL.Variant({
    'Ok' : IDL.Record({
      'llmCanisterId' : IDL.Text,
      'controllerCanisterEntry' : OfficialMainerAgentCanister,
    }),
    'Err' : ApiError,
  });
  const MainerAgentCanisterResult = IDL.Variant({
    'Ok' : OfficialMainerAgentCanister,
    'Err' : ApiError,
  });
  const CanisterInput = IDL.Record({
    'canisterType' : ProtocolCanisterType,
    'address' : CanisterAddress,
  });
  const StatusCodeRecord = IDL.Record({ 'status_code' : StatusCode });
  const StatusCodeRecordResult = IDL.Variant({
    'Ok' : StatusCodeRecord,
    'Err' : ApiError,
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
  const ScoredResponseInput = IDL.Record({
    'challengeClosedTimestamp' : IDL.Opt(IDL.Nat64),
    'challengeTopicStatus' : ChallengeTopicStatus,
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeCreationTimestamp' : IDL.Nat64,
    'challengeCreatedBy' : CanisterAddress,
    'challengeTopicId' : IDL.Text,
    'judgedBy' : IDL.Principal,
    'submittedTimestamp' : IDL.Nat64,
    'submittedBy' : IDL.Principal,
    'challengeStatus' : ChallengeStatus,
    'challengeQuestionSeed' : IDL.Nat32,
    'submissionStatus' : ChallengeResponseSubmissionStatus,
    'score' : IDL.Nat,
    'challengeQuestion' : IDL.Text,
    'challengeId' : IDL.Text,
    'challengeQueuedBy' : IDL.Principal,
    'challengeQueuedId' : IDL.Text,
    'challengeQueuedTo' : IDL.Principal,
    'challengeTopic' : IDL.Text,
    'submissionId' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'submissionCyclesRequired' : IDL.Nat,
    'challengeAnswer' : IDL.Text,
    'challengeQueuedTimestamp' : IDL.Nat64,
    'scoreSeed' : IDL.Nat32,
  });
  const ScoredResponseReturn = IDL.Record({ 'success' : IDL.Bool });
  const ScoredResponseResult = IDL.Variant({
    'Ok' : ScoredResponseReturn,
    'Err' : ApiError,
  });
  const MainerCreationInput = IDL.Record({
    'owner' : IDL.Opt(IDL.Principal),
    'paymentTransactionBlockId' : IDL.Nat64,
    'mainerConfig' : MainerConfigurationInput,
  });
  const DeriveWasmHashInput = IDL.Record({
    'textNote' : IDL.Text,
    'address' : CanisterAddress,
  });
  const CanisterWasmHashRecord = IDL.Record({
    'creationTimestamp' : IDL.Nat64,
    'wasmHash' : IDL.Vec(IDL.Nat8),
    'createdBy' : IDL.Principal,
    'textNote' : IDL.Text,
    'version' : IDL.Nat,
  });
  const CanisterWasmHashRecordResult = IDL.Variant({
    'Ok' : CanisterWasmHashRecord,
    'Err' : ApiError,
  });
  const ChallengesResult = IDL.Variant({
    'Ok' : IDL.Vec(Challenge),
    'Err' : ApiError,
  });
  const GameStateTresholds = IDL.Record({
    'thresholdMaxOpenSubmissions' : IDL.Nat,
    'thresholdMaxOpenChallenges' : IDL.Nat,
    'thresholdArchiveClosedChallenges' : IDL.Nat,
    'thresholdScoredResponsesPerChallenge' : IDL.Nat,
  });
  const GameStateTresholdsResult = IDL.Variant({
    'Ok' : GameStateTresholds,
    'Err' : ApiError,
  });
  const CanisterRetrieveInput = IDL.Record({ 'address' : CanisterAddress });
  const MainerAgentCanistersResult = IDL.Variant({
    'Ok' : IDL.Vec(OfficialMainerAgentCanister),
    'Err' : ApiError,
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
    'challengeQueuedBy' : IDL.Principal,
    'challengeQueuedId' : IDL.Text,
    'challengeQueuedTo' : IDL.Principal,
    'challengeTopic' : IDL.Text,
    'submissionId' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'submissionCyclesRequired' : IDL.Nat,
    'challengeAnswer' : IDL.Text,
    'challengeQueuedTimestamp' : IDL.Nat64,
  });
  const ChallengeResponseSubmissionResult = IDL.Variant({
    'Ok' : ChallengeResponseSubmission,
    'Err' : ApiError,
  });
  const NatResult = IDL.Variant({ 'Ok' : IDL.Nat, 'Err' : ApiError });
  const OfficialProtocolCanister = IDL.Record({
    'status' : CanisterStatus,
    'canisterType' : ProtocolCanisterType,
    'ownedBy' : IDL.Principal,
    'creationTimestamp' : IDL.Nat64,
    'createdBy' : IDL.Principal,
    'address' : CanisterAddress,
  });
  const AuthRecord = IDL.Record({ 'auth' : IDL.Text });
  const AuthRecordResult = IDL.Variant({ 'Ok' : AuthRecord, 'Err' : ApiError });
  const ChallengeResponseSubmissionsResult = IDL.Variant({
    'Ok' : IDL.Vec(ChallengeResponseSubmission),
    'Err' : ApiError,
  });
  const CyclesBurntResult = IDL.Variant({ 'Ok' : IDL.Nat, 'Err' : ApiError });
  const ChallengeResult = IDL.Variant({ 'Ok' : Challenge, 'Err' : ApiError });
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
  List_1.fill(IDL.Opt(IDL.Tuple(ChallengeParticipantEntry, List_1)));
  const ChallengeWinnerDeclaration = IDL.Record({
    'participants' : List_1,
    'thirdPlace' : ChallengeParticipantEntry,
    'winner' : ChallengeParticipantEntry,
    'secondPlace' : ChallengeParticipantEntry,
    'finalizedTimestamp' : IDL.Nat64,
    'challengeId' : IDL.Text,
  });
  const ChallengeWinnersResult = IDL.Variant({
    'Ok' : IDL.Vec(ChallengeWinnerDeclaration),
    'Err' : ApiError,
  });
  const ProtocolActivityRecord = IDL.Record({
    'challenges' : IDL.Vec(Challenge),
    'winners' : IDL.Vec(ChallengeWinnerDeclaration),
  });
  const ProtocolActivityResult = IDL.Variant({
    'Ok' : ProtocolActivityRecord,
    'Err' : ApiError,
  });
  const SubmissionRetrievalInput = IDL.Record({
    'challengeId' : IDL.Text,
    'submissionId' : IDL.Text,
  });
  const ScoredResponse = IDL.Record({
    'challengeClosedTimestamp' : IDL.Opt(IDL.Nat64),
    'challengeTopicStatus' : ChallengeTopicStatus,
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeCreationTimestamp' : IDL.Nat64,
    'challengeCreatedBy' : CanisterAddress,
    'challengeTopicId' : IDL.Text,
    'judgedBy' : IDL.Principal,
    'submittedTimestamp' : IDL.Nat64,
    'submittedBy' : IDL.Principal,
    'challengeStatus' : ChallengeStatus,
    'challengeQuestionSeed' : IDL.Nat32,
    'submissionStatus' : ChallengeResponseSubmissionStatus,
    'score' : IDL.Nat,
    'challengeQuestion' : IDL.Text,
    'challengeId' : IDL.Text,
    'challengeQueuedBy' : IDL.Principal,
    'challengeQueuedId' : IDL.Text,
    'challengeQueuedTo' : IDL.Principal,
    'challengeTopic' : IDL.Text,
    'judgedTimestamp' : IDL.Nat64,
    'submissionId' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'submissionCyclesRequired' : IDL.Nat,
    'challengeAnswer' : IDL.Text,
    'challengeQueuedTimestamp' : IDL.Nat64,
    'scoreSeed' : IDL.Nat32,
  });
  const ScoredResponseRetrievalResult = IDL.Variant({
    'Ok' : ScoredResponse,
    'Err' : ApiError,
  });
  List.fill(IDL.Opt(IDL.Tuple(ScoredResponse, List)));
  const ScoredChallengesResult = IDL.Variant({
    'Ok' : IDL.Vec(IDL.Tuple(IDL.Text, List)),
    'Err' : ApiError,
  });
  const UpdateWasmHashInput = IDL.Record({
    'wasmHash' : IDL.Vec(IDL.Nat8),
    'textNote' : IDL.Text,
  });
  const ChallengeResponseSubmissionInput = IDL.Record({
    'challengeClosedTimestamp' : IDL.Opt(IDL.Nat64),
    'challengeTopicStatus' : ChallengeTopicStatus,
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeCreationTimestamp' : IDL.Nat64,
    'challengeCreatedBy' : CanisterAddress,
    'challengeTopicId' : IDL.Text,
    'submittedBy' : IDL.Principal,
    'challengeStatus' : ChallengeStatus,
    'challengeQuestionSeed' : IDL.Nat32,
    'challengeQuestion' : IDL.Text,
    'challengeId' : IDL.Text,
    'challengeQueuedBy' : IDL.Principal,
    'challengeQueuedId' : IDL.Text,
    'challengeQueuedTo' : IDL.Principal,
    'challengeTopic' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'submissionCyclesRequired' : IDL.Nat,
    'challengeAnswer' : IDL.Text,
    'challengeQueuedTimestamp' : IDL.Nat64,
  });
  const ChallengeResponseSubmissionMetadata = IDL.Record({
    'submittedTimestamp' : IDL.Nat64,
    'submissionStatus' : ChallengeResponseSubmissionStatus,
    'submissionId' : IDL.Text,
  });
  const ChallengeResponseSubmissionMetadataResult = IDL.Variant({
    'Ok' : ChallengeResponseSubmissionMetadata,
    'Err' : ApiError,
  });
  const MainerAgentTopUpInput = IDL.Record({
    'paymentTransactionBlockId' : IDL.Nat64,
    'mainerAgent' : OfficialMainerAgentCanister,
  });
  const GameStateCanister = IDL.Service({
    'addChallenge' : IDL.Func(
        [NewChallengeInput],
        [ChallengeAdditionResult],
        [],
      ),
    'addChallengeTopic' : IDL.Func(
        [ChallengeTopicInput],
        [ChallengeTopicResult],
        [],
      ),
    'addLlmCanisterToMainer' : IDL.Func(
        [OfficialMainerAgentCanister],
        [SetUpMainerLlmCanisterResult],
        [],
      ),
    'addMainerAgentCanister' : IDL.Func(
        [OfficialMainerAgentCanister],
        [MainerAgentCanisterResult],
        [],
      ),
    'addMainerAgentCanisterAdmin' : IDL.Func(
        [OfficialMainerAgentCanister],
        [MainerAgentCanisterResult],
        [],
      ),
    'addOfficialCanister' : IDL.Func(
        [CanisterInput],
        [StatusCodeRecordResult],
        [],
      ),
    'addScoredResponse' : IDL.Func(
        [ScoredResponseInput],
        [ScoredResponseResult],
        [],
      ),
    'createUserMainerAgent' : IDL.Func(
        [MainerCreationInput],
        [MainerAgentCanisterResult],
        [],
      ),
    'deriveNewMainerAgentCanisterWasmHashAdmin' : IDL.Func(
        [DeriveWasmHashInput],
        [CanisterWasmHashRecordResult],
        [],
      ),
    'getCanisterPrincipal' : IDL.Func([], [IDL.Text], ['query']),
    'getCurrentChallenges' : IDL.Func([], [ChallengesResult], ['query']),
    'getCurrentChallengesAdmin' : IDL.Func([], [ChallengesResult], ['query']),
    'getGameStateThresholdsAdmin' : IDL.Func(
        [],
        [GameStateTresholdsResult],
        ['query'],
      ),
    'getMainerAgentCanisterInfo' : IDL.Func(
        [CanisterRetrieveInput],
        [MainerAgentCanisterResult],
        ['query'],
      ),
    'getMainerAgentCanistersForUser' : IDL.Func(
        [],
        [MainerAgentCanistersResult],
        ['query'],
      ),
    'getNextSubmissionToJudge' : IDL.Func(
        [],
        [ChallengeResponseSubmissionResult],
        [],
      ),
    'getNumCurrentChallengesAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumOpenSubmissionsAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumScoredChallengesAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumSubmissionsAdmin' : IDL.Func([], [NatResult], ['query']),
    'getOfficialCanistersAdmin' : IDL.Func(
        [],
        [IDL.Vec(OfficialProtocolCanister)],
        ['query'],
      ),
    'getOfficialChallengerCanisters' : IDL.Func([], [AuthRecordResult], []),
    'getOfficialSharedServiceCanisters' : IDL.Func([], [AuthRecordResult], []),
    'getOpenSubmissionsAdmin' : IDL.Func(
        [],
        [ChallengeResponseSubmissionsResult],
        ['query'],
      ),
    'getProtocolTotalCyclesBurnt' : IDL.Func(
        [],
        [CyclesBurntResult],
        ['query'],
      ),
    'getRandomOpenChallenge' : IDL.Func([], [ChallengeResult], []),
    'getRandomOpenChallengeTopic' : IDL.Func([], [ChallengeTopicResult], []),
    'getRecentChallengeWinners' : IDL.Func(
        [],
        [ChallengeWinnersResult],
        ['query'],
      ),
    'getRecentProtocolActivity' : IDL.Func(
        [],
        [ProtocolActivityResult],
        ['query'],
      ),
    'getRecentProtocolActivity_mockup' : IDL.Func(
        [],
        [ProtocolActivityResult],
        ['query'],
      ),
    'getScoreForSubmission' : IDL.Func(
        [SubmissionRetrievalInput],
        [ScoredResponseRetrievalResult],
        ['query'],
      ),
    'getScoreForSubmission_mockup' : IDL.Func(
        [SubmissionRetrievalInput],
        [ScoredResponseRetrievalResult],
        ['query'],
      ),
    'getScoredChallengesAdmin' : IDL.Func(
        [],
        [ScoredChallengesResult],
        ['query'],
      ),
    'getSubmissionsAdmin' : IDL.Func(
        [],
        [ChallengeResponseSubmissionsResult],
        ['query'],
      ),
    'health' : IDL.Func([], [StatusCodeRecordResult], ['query']),
    'removeOfficialSharedServiceCanisters' : IDL.Func(
        [IDL.Text],
        [AuthRecordResult],
        [],
      ),
    'setGameStateThresholdsAdmin' : IDL.Func(
        [GameStateTresholds],
        [StatusCodeRecordResult],
        [],
      ),
    'setInitialChallengeTopics' : IDL.Func([], [StatusCodeRecordResult], []),
    'setOfficialMainerAgentCanisterWasmHashAdmin' : IDL.Func(
        [UpdateWasmHashInput],
        [CanisterWasmHashRecordResult],
        [],
      ),
    'setTokenLedgerCanisterId' : IDL.Func([IDL.Text], [AuthRecordResult], []),
    'setUpMainerLlmCanister' : IDL.Func(
        [OfficialMainerAgentCanister],
        [SetUpMainerLlmCanisterResult],
        [],
      ),
    'spinUpMainerControllerCanister' : IDL.Func(
        [OfficialMainerAgentCanister],
        [MainerAgentCanisterResult],
        [],
      ),
    'submitChallengeResponse' : IDL.Func(
        [ChallengeResponseSubmissionInput],
        [ChallengeResponseSubmissionMetadataResult],
        [],
      ),
    'testMainerCodeIntegrityAdmin' : IDL.Func([], [AuthRecordResult], []),
    'testTokenMintingAdmin' : IDL.Func([], [AuthRecordResult], []),
    'topUpCyclesForMainerAgent' : IDL.Func(
        [MainerAgentTopUpInput],
        [MainerAgentCanisterResult],
        [],
      ),
    'unlockUserMainerAgent' : IDL.Func(
        [MainerCreationInput],
        [MainerAgentCanisterResult],
        [],
      ),
  });
  return GameStateCanister;
};
export const init = ({ IDL }) => { return []; };
