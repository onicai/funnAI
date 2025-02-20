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
  const ProtocolCanisterType = IDL.Variant({
    'MainerAgent' : IDL.Null,
    'Challenger' : IDL.Null,
    'Judge' : IDL.Null,
    'Verifier' : IDL.Null,
    'MainerCreator' : IDL.Null,
  });
  const MainerAgentCanisterInput = IDL.Record({
    'canisterType' : ProtocolCanisterType,
    'ownedBy' : IDL.Principal,
    'address' : CanisterAddress,
  });
  const OfficialProtocolCanister = IDL.Record({
    'canisterType' : ProtocolCanisterType,
    'ownedBy' : IDL.Principal,
    'creationTimestamp' : IDL.Nat64,
    'createdBy' : IDL.Principal,
    'address' : CanisterAddress,
  });
  const MainerAgentCanisterResult = IDL.Variant({
    'Ok' : OfficialProtocolCanister,
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
    'challengeTopic' : IDL.Text,
    'submissionId' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'submissionCyclesRequired' : IDL.Nat,
    'challengeAnswer' : IDL.Text,
    'scoreSeed' : IDL.Nat32,
  });
  const ScoredResponseReturn = IDL.Record({ 'success' : IDL.Bool });
  const ScoredResponseResult = IDL.Variant({
    'Ok' : ScoredResponseReturn,
    'Err' : ApiError,
  });
  const SelectableMainerLLM = IDL.Variant({ 'Qwen2_5_0_5_B' : IDL.Null });
  const MainerConfigurationInput = IDL.Record({
    'aiModel' : IDL.Opt(SelectableMainerLLM),
  });
  const ChallengesResult = IDL.Variant({
    'Ok' : IDL.Vec(Challenge),
    'Err' : ApiError,
  });
  const CanisterRetrieveInput = IDL.Record({ 'address' : CanisterAddress });
  const MainerAgentCanistersResult = IDL.Variant({
    'Ok' : IDL.Vec(OfficialProtocolCanister),
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
    'challengeTopic' : IDL.Text,
    'submissionId' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'submissionCyclesRequired' : IDL.Nat,
    'challengeAnswer' : IDL.Text,
  });
  const ChallengeResponseSubmissionResult = IDL.Variant({
    'Ok' : ChallengeResponseSubmission,
    'Err' : ApiError,
  });
  const AuthRecord = IDL.Record({ 'auth' : IDL.Text });
  const AuthRecordResult = IDL.Variant({ 'Ok' : AuthRecord, 'Err' : ApiError });
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
    'challengeTopic' : IDL.Text,
    'judgedTimestamp' : IDL.Nat64,
    'submissionId' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'submissionCyclesRequired' : IDL.Nat,
    'challengeAnswer' : IDL.Text,
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
  const ChallengeResponseSubmissionsResult = IDL.Variant({
    'Ok' : IDL.Vec(ChallengeResponseSubmission),
    'Err' : ApiError,
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
    'challengeTopic' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'submissionCyclesRequired' : IDL.Nat,
    'challengeAnswer' : IDL.Text,
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
    'addMainerAgentCanister' : IDL.Func(
        [MainerAgentCanisterInput],
        [MainerAgentCanisterResult],
        [],
      ),
    'addMainerAgentCanisterAdmin' : IDL.Func(
        [MainerAgentCanisterInput],
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
    'createUserMainerAgentCanister' : IDL.Func(
        [MainerConfigurationInput],
        [MainerAgentCanisterResult],
        [],
      ),
    'getCurrentChallenges' : IDL.Func([], [ChallengesResult], ['query']),
    'getCurrentChallengesAdmin' : IDL.Func([], [ChallengesResult], ['query']),
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
    'getOfficialChallengerCanisters' : IDL.Func([], [AuthRecordResult], []),
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
    'getScoreForSubmission' : IDL.Func(
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
    'setInitialChallengeTopics' : IDL.Func([], [StatusCodeRecordResult], []),
    'submitChallengeResponse' : IDL.Func(
        [ChallengeResponseSubmissionInput],
        [ChallengeResponseSubmissionMetadataResult],
        [],
      ),
  });
  return GameStateCanister;
};
export const init = ({ IDL }) => { return []; };
