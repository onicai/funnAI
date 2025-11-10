export const idlFactory = ({ IDL }) => {
  const List = IDL.Rec();
  const List_1 = IDL.Rec();
  const Value__1 = IDL.Rec();
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
    'mainerPromptId' : IDL.Text,
    'mainerMaxContinueLoopCount' : IDL.Nat,
    'mainerTemp' : IDL.Float64,
    'challengeQuestionSeed' : IDL.Nat32,
    'mainerNumTokens' : IDL.Nat64,
    'challengeQuestion' : IDL.Text,
    'challengeTopic' : IDL.Text,
    'cyclesGenerateChallengeChctrlChllm' : IDL.Nat,
    'judgePromptId' : IDL.Text,
    'cyclesGenerateChallengeGsChctrl' : IDL.Nat,
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
    'cyclesGenerateChallengeChctrlChllm' : IDL.Nat,
    'cyclesGenerateChallengeGsChctrl' : IDL.Nat,
  });
  const ChallengeTopicResult = IDL.Variant({
    'Ok' : ChallengeTopic,
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
    'subnet' : IDL.Text,
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
    'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : IDL.Nat,
    'protocolOperationFeesCut' : IDL.Nat,
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeCreationTimestamp' : IDL.Nat64,
    'challengeCreatedBy' : CanisterAddress,
    'challengeTopicId' : IDL.Text,
    'cyclesGenerateResponseOwnctrlOwnllmHIGH' : IDL.Nat,
    'judgedBy' : IDL.Principal,
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
    'score' : IDL.Nat,
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
    'scoreSeed' : IDL.Nat32,
    'cyclesGenerateChallengeGsChctrl' : IDL.Nat,
    'cyclesGenerateScoreJuctrlJullm' : IDL.Nat,
    'cyclesGenerateResponseSsctrlGs' : IDL.Nat,
  });
  const ScoredResponseReturn = IDL.Record({ 'success' : IDL.Bool });
  const ScoredResponseResult = IDL.Variant({
    'Ok' : ScoredResponseReturn,
    'Err' : ApiError,
  });
  const NatResult = IDL.Variant({ 'Ok' : IDL.Nat, 'Err' : ApiError });
  const AuthRecord = IDL.Record({ 'auth' : IDL.Text });
  const AuthRecordResult = IDL.Variant({ 'Ok' : AuthRecord, 'Err' : ApiError });
  const MainerMarketplaceReservationInput = IDL.Record({
    'address' : CanisterAddress,
  });
  const MainerMarketplaceListing = IDL.Record({
    'listedTimestamp' : IDL.Nat64,
    'listedBy' : IDL.Principal,
    'mainerType' : MainerAgentCanisterType,
    'address' : CanisterAddress,
    'reservedBy' : IDL.Opt(IDL.Principal),
    'priceE8S' : IDL.Nat,
  });
  const MainerMarketplaceReservationResult = IDL.Variant({
    'Ok' : MainerMarketplaceListing,
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
  const DownloadJudgePromptCacheBytesChunkInput = IDL.Record({
    'chunkID' : IDL.Nat,
    'judgePromptId' : IDL.Text,
  });
  const DownloadJudgePromptCacheBytesChunkRecord = IDL.Record({
    'chunkID' : IDL.Nat,
    'bytesChunk' : IDL.Vec(IDL.Nat8),
    'judgePromptId' : IDL.Text,
  });
  const DownloadJudgePromptCacheBytesChunkRecordResult = IDL.Variant({
    'Ok' : DownloadJudgePromptCacheBytesChunkRecord,
    'Err' : ApiError,
  });
  const DownloadMainerPromptCacheBytesChunkInput = IDL.Record({
    'mainerPromptId' : IDL.Text,
    'chunkID' : IDL.Nat,
  });
  const DownloadMainerPromptCacheBytesChunkRecord = IDL.Record({
    'mainerPromptId' : IDL.Text,
    'chunkID' : IDL.Nat,
    'bytesChunk' : IDL.Vec(IDL.Nat8),
  });
  const DownloadMainerPromptCacheBytesChunkRecordResult = IDL.Variant({
    'Ok' : DownloadMainerPromptCacheBytesChunkRecord,
    'Err' : ApiError,
  });
  const FinishUploadJudgePromptCacheInput = IDL.Record({
    'promptCacheFilename' : IDL.Text,
    'promptText' : IDL.Text,
    'judgePromptId' : IDL.Text,
    'promptCacheSha256' : IDL.Text,
  });
  const FinishUploadMainerPromptCacheInput = IDL.Record({
    'promptCacheFilename' : IDL.Text,
    'mainerPromptId' : IDL.Text,
    'promptText' : IDL.Text,
    'promptCacheSha256' : IDL.Text,
  });
  const ChallengesResult = IDL.Variant({
    'Ok' : IDL.Vec(Challenge),
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
  const CyclesBurnRateResult = IDL.Variant({
    'Ok' : CyclesBurnRate,
    'Err' : ApiError,
  });
  const CyclesFlow = IDL.Record({
    'costCreateMcMainerLlm' : IDL.Nat,
    'cyclesCreateMainerMarginGs' : IDL.Nat,
    'costCreateMainerCtrl' : IDL.Nat,
    'costCreateMcMainerCtrl' : IDL.Nat,
    'cyclesBurntChallengeGeneration' : IDL.Nat,
    'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : IDL.Nat,
    'protocolOperationFeesCut' : IDL.Nat,
    'dailyChallenges' : IDL.Nat,
    'dailySubmissionsPerShareMEDIUM' : IDL.Nat,
    'cyclesBurntResponseGenerationShare' : IDL.Nat,
    'numShareServiceLlms' : IDL.Nat,
    'numChallengerLlms' : IDL.Nat,
    'costIdleBurnRateJuctrl' : IDL.Nat,
    'cyclesGenerateResponseOwnctrlOwnllmHIGH' : IDL.Nat,
    'cyclesBurntResponseGenerationOwn' : IDL.Nat,
    'dailySubmissionsPerShareLOW' : IDL.Nat,
    'cyclesGenerateResponseOwnctrlOwnllmLOW' : IDL.Nat,
    'costGenerateResponseOwnctrl' : IDL.Nat,
    'costGenerateChallengeChctrl' : IDL.Nat,
    'costIdleBurnRateSactrl' : IDL.Nat,
    'dailySubmissionsPerOwnLOW' : IDL.Nat,
    'cyclesGenerateResponseSsctrlSsllm' : IDL.Nat,
    'costIdleBurnRateOwnctrl' : IDL.Nat,
    'dailySubmissionsPerOwnMEDIUM' : IDL.Nat,
    'costIdleBurnRateChllm' : IDL.Nat,
    'cyclesCreateMainerLlmTargetBalance' : IDL.Nat,
    'cyclesGenerateResponseOwnctrlGs' : IDL.Nat,
    'costIdleBurnRateOwnllm' : IDL.Nat,
    'dailySubmissionsPerShareHIGH' : IDL.Nat,
    'costIdleBurnRateJullm' : IDL.Nat,
    'costIdleBurnRateGs' : IDL.Nat,
    'costIdleBurnRateMc' : IDL.Nat,
    'marginCost' : IDL.Nat,
    'costGenerateResponseShareGs' : IDL.Nat,
    'costGenerateChallengeGs' : IDL.Nat,
    'costGenerateResponseSactrl' : IDL.Nat,
    'costIdleBurnRateSallm' : IDL.Nat,
    'cyclesCreatemMainerMarginMc' : IDL.Nat,
    'cyclesGenerateChallengeChctrlChllm' : IDL.Nat,
    'costGenerateResponseOwnGs' : IDL.Nat,
    'costIdleBurnRateSsllm' : IDL.Nat,
    'dailySubmissionsPerOwnHIGH' : IDL.Nat,
    'costGenerateResponseOwnllm' : IDL.Nat,
    'dailySubmissionsAllShare' : IDL.Nat,
    'cyclesGenerateScoreGsJuctrl' : IDL.Nat,
    'cyclesBurntJudgeScoring' : IDL.Nat,
    'cyclesGenerateResponseSactrlSsctrl' : IDL.Nat,
    'costGenerateScoreJullm' : IDL.Nat,
    'submissionFee' : IDL.Nat,
    'costIdleBurnRateSsctrl' : IDL.Nat,
    'costUpgradeMainerCtrl' : IDL.Nat,
    'costGenerateScoreGs' : IDL.Nat,
    'cyclesFailedSubmissionCut' : IDL.Nat,
    'costGenerateScoreJuctrl' : IDL.Nat,
    'costGenerateChallengeChllm' : IDL.Nat,
    'costUpgradeMcMainerLlm' : IDL.Nat,
    'costUpgradeMainerLlm' : IDL.Nat,
    'dailySubmissionsAllOwn' : IDL.Nat,
    'cyclesSubmitResponse' : IDL.Nat,
    'cyclesGenerateChallengeGsChctrl' : IDL.Nat,
    'cyclesGenerateScoreJuctrlJullm' : IDL.Nat,
    'costGenerateResponseSsctrl' : IDL.Nat,
    'costGenerateResponseSsllm' : IDL.Nat,
    'marginFailedSubmissionCut' : IDL.Nat,
    'numJudgeLlms' : IDL.Nat,
    'costUpgradeMcMainerCtrl' : IDL.Nat,
    'costIdleBurnRateChctrl' : IDL.Nat,
    'cyclesGenerateResponseSsctrlGs' : IDL.Nat,
    'costCreateMainerLlm' : IDL.Nat,
  });
  const CyclesFlowResult = IDL.Variant({ 'Ok' : CyclesFlow, 'Err' : ApiError });
  const CyclesTransaction = IDL.Record({
    'newOfficialCycleBalance' : IDL.Nat,
    'creationTimestamp' : IDL.Nat64,
    'amountAdded' : IDL.Nat,
    'sentBy' : IDL.Principal,
    'previousCyclesBalance' : IDL.Nat,
    'succeeded' : IDL.Bool,
  });
  const CyclesTransactionsResult = IDL.Variant({
    'Ok' : IDL.Vec(CyclesTransaction),
    'Err' : ApiError,
  });
  const FlagRecord = IDL.Record({ 'flag' : IDL.Bool });
  const FlagResult = IDL.Variant({ 'Ok' : FlagRecord, 'Err' : ApiError });
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
  const JudgePromptInfo = IDL.Record({
    'promptCacheFilename' : IDL.Text,
    'promptText' : IDL.Text,
    'promptCacheNumberOfChunks' : IDL.Nat,
    'promptCacheSha256' : IDL.Text,
  });
  const JudgePromptInfoResult = IDL.Variant({
    'Ok' : JudgePromptInfo,
    'Err' : ApiError,
  });
  const CheckMainerLimit = IDL.Record({
    'mainerType' : MainerAgentCanisterType,
  });
  const CanisterRetrieveInput = IDL.Record({ 'address' : CanisterAddress });
  const MainerAgentCanistersResult = IDL.Variant({
    'Ok' : IDL.Vec(OfficialMainerAgentCanister),
    'Err' : ApiError,
  });
  const MainerAuctionTimerInfoRecord = IDL.Record({
    'active' : IDL.Bool,
    'intervalSeconds' : IDL.Nat,
    'lastUpdateNs' : IDL.Nat,
  });
  const MainerAuctionTimerInfoResult = IDL.Variant({
    'Ok' : MainerAuctionTimerInfoRecord,
    'Err' : ApiError,
  });
  const MainerPromptInfo = IDL.Record({
    'promptCacheFilename' : IDL.Text,
    'promptText' : IDL.Text,
    'promptCacheNumberOfChunks' : IDL.Nat,
    'promptCacheSha256' : IDL.Text,
  });
  const MainerPromptInfoResult = IDL.Variant({
    'Ok' : MainerPromptInfo,
    'Err' : ApiError,
  });
  const MainerMarketplaceListingsResult = IDL.Variant({
    'Ok' : IDL.Vec(MainerMarketplaceListing),
    'Err' : ApiError,
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
  const ChallengeResponseSubmissionWithQueueStatus = IDL.Record({
    'remainingInQueue' : IDL.Nat,
    'submission' : ChallengeResponseSubmission,
  });
  const ChallengeResponseSubmissionWithQueueStatusResult = IDL.Variant({
    'Ok' : ChallengeResponseSubmissionWithQueueStatus,
    'Err' : ApiError,
  });
  const OfficialProtocolCanister = IDL.Record({
    'status' : CanisterStatus,
    'canisterType' : ProtocolCanisterType,
    'ownedBy' : IDL.Principal,
    'creationTimestamp' : IDL.Nat64,
    'createdBy' : IDL.Principal,
    'subnet' : IDL.Text,
    'address' : CanisterAddress,
  });
  const ChallengeResponseSubmissionsResult = IDL.Variant({
    'Ok' : IDL.Vec(ChallengeResponseSubmission),
    'Err' : ApiError,
  });
  const PriceRecord = IDL.Record({ 'price' : IDL.Nat64 });
  const PriceResult = IDL.Variant({ 'Ok' : PriceRecord, 'Err' : ApiError });
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
  const PaymentTransactionBlockId = IDL.Record({
    'paymentTransactionBlockId' : IDL.Nat64,
  });
  const RedeemedForOptions = IDL.Variant({
    'MainerCreation' : MainerAgentCanisterType,
    'MainerTopUp' : CanisterAddress,
  });
  const RedeemedTransactionBlock = IDL.Record({
    'redeemedBy' : IDL.Principal,
    'creationTimestamp' : IDL.Nat64,
    'paymentTransactionBlockId' : IDL.Nat64,
    'redeemedFor' : RedeemedForOptions,
    'amount' : IDL.Nat,
  });
  const RedeemedTransactionBlockResult = IDL.Variant({
    'Ok' : RedeemedTransactionBlock,
    'Err' : ApiError,
  });
  const RedeemedTransactionBlocksResult = IDL.Variant({
    'Ok' : IDL.Vec(RedeemedTransactionBlock),
    'Err' : ApiError,
  });
  const RewardPerChallenge = IDL.Record({
    'amountForAllParticipants' : IDL.Nat,
    'thirdPlaceAmount' : IDL.Nat,
    'rewardType' : RewardType,
    'totalAmount' : IDL.Nat,
    'winnerAmount' : IDL.Nat,
    'secondPlaceAmount' : IDL.Nat,
  });
  const RewardPerChallengeResult = IDL.Variant({
    'Ok' : RewardPerChallenge,
    'Err' : ApiError,
  });
  const SubmissionRetrievalInput = IDL.Record({
    'challengeId' : IDL.Text,
    'submissionId' : IDL.Text,
  });
  const ScoredResponse = IDL.Record({
    'challengeClosedTimestamp' : IDL.Opt(IDL.Nat64),
    'challengeTopicStatus' : ChallengeTopicStatus,
    'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : IDL.Nat,
    'protocolOperationFeesCut' : IDL.Nat,
    'challengeTopicCreationTimestamp' : IDL.Nat64,
    'challengeCreationTimestamp' : IDL.Nat64,
    'challengeCreatedBy' : CanisterAddress,
    'challengeTopicId' : IDL.Text,
    'cyclesGenerateResponseOwnctrlOwnllmHIGH' : IDL.Nat,
    'judgedBy' : IDL.Principal,
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
    'score' : IDL.Nat,
    'challengeQuestion' : IDL.Text,
    'challengeId' : IDL.Text,
    'challengeQueuedBy' : IDL.Principal,
    'challengeQueuedId' : IDL.Text,
    'challengeQueuedTo' : IDL.Principal,
    'challengeTopic' : IDL.Text,
    'judgedTimestamp' : IDL.Nat64,
    'cyclesGenerateChallengeChctrlChllm' : IDL.Nat,
    'cyclesGenerateScoreGsJuctrl' : IDL.Nat,
    'cyclesGenerateResponseSactrlSsctrl' : IDL.Nat,
    'judgePromptId' : IDL.Text,
    'submissionId' : IDL.Text,
    'challengeAnswerSeed' : IDL.Nat32,
    'challengeAnswer' : IDL.Text,
    'challengeQueuedTimestamp' : IDL.Nat64,
    'cyclesSubmitResponse' : IDL.Nat,
    'scoreSeed' : IDL.Nat32,
    'cyclesGenerateChallengeGsChctrl' : IDL.Nat,
    'cyclesGenerateScoreJuctrlJullm' : IDL.Nat,
    'cyclesGenerateResponseSsctrlGs' : IDL.Nat,
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
  const OfficialProtocolCanistersResult = IDL.Variant({
    'Ok' : IDL.Vec(OfficialProtocolCanister),
    'Err' : ApiError,
  });
  const SubnetIds = IDL.Record({
    'subnetShareServiceCtrl' : IDL.Text,
    'subnetShareAgentCtrl' : IDL.Text,
    'subnetShareServiceLlm' : IDL.Text,
  });
  const SubnetIdsResult = IDL.Variant({ 'Ok' : SubnetIds, 'Err' : ApiError });
  const SupportedStandards = IDL.Vec(
    IDL.Record({ 'url' : IDL.Text, 'name' : IDL.Text })
  );
  const Subaccount = IDL.Vec(IDL.Nat8);
  const Account__1 = IDL.Record({
    'owner' : IDL.Principal,
    'subaccount' : IDL.Opt(Subaccount),
  });
  const ApprovalInfo = IDL.Record({
    'memo' : IDL.Opt(IDL.Vec(IDL.Nat8)),
    'from_subaccount' : IDL.Opt(IDL.Vec(IDL.Nat8)),
    'created_at_time' : IDL.Opt(IDL.Nat64),
    'expires_at' : IDL.Opt(IDL.Nat64),
    'spender' : Account__1,
  });
  const ApproveTokenArg = IDL.Record({
    'token_id' : IDL.Nat,
    'approval_info' : ApprovalInfo,
  });
  const ApproveTokenError = IDL.Variant({
    'GenericError' : IDL.Record({
      'message' : IDL.Text,
      'error_code' : IDL.Nat,
    }),
    'Duplicate' : IDL.Record({ 'duplicate_of' : IDL.Nat }),
    'InvalidSpender' : IDL.Null,
    'NonExistingTokenId' : IDL.Null,
    'Unauthorized' : IDL.Null,
    'CreatedInFuture' : IDL.Record({ 'ledger_time' : IDL.Nat64 }),
    'GenericBatchError' : IDL.Record({
      'message' : IDL.Text,
      'error_code' : IDL.Nat,
    }),
    'TooOld' : IDL.Null,
  });
  const ApproveTokenResult = IDL.Variant({
    'Ok' : IDL.Nat,
    'Err' : ApproveTokenError,
  });
  const RevokeTokenApprovalArg = IDL.Record({
    'token_id' : IDL.Nat,
    'memo' : IDL.Opt(IDL.Vec(IDL.Nat8)),
    'from_subaccount' : IDL.Opt(IDL.Vec(IDL.Nat8)),
    'created_at_time' : IDL.Opt(IDL.Nat64),
    'spender' : IDL.Opt(Account__1),
  });
  const RevokeTokenApprovalError = IDL.Variant({
    'GenericError' : IDL.Record({
      'message' : IDL.Text,
      'error_code' : IDL.Nat,
    }),
    'Duplicate' : IDL.Record({ 'duplicate_of' : IDL.Nat }),
    'NonExistingTokenId' : IDL.Null,
    'Unauthorized' : IDL.Null,
    'CreatedInFuture' : IDL.Record({ 'ledger_time' : IDL.Nat64 }),
    'ApprovalDoesNotExist' : IDL.Null,
    'GenericBatchError' : IDL.Record({
      'message' : IDL.Text,
      'error_code' : IDL.Nat,
    }),
    'TooOld' : IDL.Null,
  });
  const RevokeTokenApprovalResult = IDL.Variant({
    'Ok' : IDL.Nat,
    'Err' : RevokeTokenApprovalError,
  });
  const TransferFromArg = IDL.Record({
    'to' : Account__1,
    'spender_subaccount' : IDL.Opt(IDL.Vec(IDL.Nat8)),
    'token_id' : IDL.Nat,
    'from' : Account__1,
    'memo' : IDL.Opt(IDL.Vec(IDL.Nat8)),
    'created_at_time' : IDL.Opt(IDL.Nat64),
  });
  const TransferFromError = IDL.Variant({
    'GenericError' : IDL.Record({
      'message' : IDL.Text,
      'error_code' : IDL.Nat,
    }),
    'Duplicate' : IDL.Record({ 'duplicate_of' : IDL.Nat }),
    'NonExistingTokenId' : IDL.Null,
    'Unauthorized' : IDL.Null,
    'CreatedInFuture' : IDL.Record({ 'ledger_time' : IDL.Nat64 }),
    'InvalidRecipient' : IDL.Null,
    'GenericBatchError' : IDL.Record({
      'message' : IDL.Text,
      'error_code' : IDL.Nat,
    }),
    'TooOld' : IDL.Null,
  });
  const TransferFromResult = IDL.Variant({
    'Ok' : IDL.Nat,
    'Err' : TransferFromError,
  });
  const Account = IDL.Record({
    'owner' : IDL.Principal,
    'subaccount' : IDL.Opt(IDL.Vec(IDL.Nat8)),
  });
  Value__1.fill(
    IDL.Variant({
      'Int' : IDL.Int,
      'Map' : IDL.Vec(IDL.Tuple(IDL.Text, Value__1)),
      'Nat' : IDL.Nat,
      'Blob' : IDL.Vec(IDL.Nat8),
      'Text' : IDL.Text,
      'Array' : IDL.Vec(Value__1),
    })
  );
  const Value = IDL.Variant({
    'Int' : IDL.Int,
    'Map' : IDL.Vec(IDL.Tuple(IDL.Text, Value__1)),
    'Nat' : IDL.Nat,
    'Blob' : IDL.Vec(IDL.Nat8),
    'Text' : IDL.Text,
    'Array' : IDL.Vec(Value__1),
  });
  const MainerctrlReinstallInput = IDL.Record({
    'canisterAddress' : CanisterAddress,
  });
  const TextResult = IDL.Variant({ 'Ok' : IDL.Text, 'Err' : ApiError });
  const SetCyclesBurnRateInput = IDL.Record({
    'cyclesBurnRate' : CyclesBurnRate,
    'cyclesBurnRateDefault' : CyclesBurnRateDefault,
  });
  const CyclesFlowSettings = IDL.Record({
    'costCreateMcMainerLlm' : IDL.Opt(IDL.Nat),
    'cyclesCreateMainerMarginGs' : IDL.Opt(IDL.Nat),
    'costCreateMainerCtrl' : IDL.Opt(IDL.Nat),
    'cyclesUpgradeMainerllmMcMainerllm' : IDL.Opt(IDL.Nat),
    'costCreateMcMainerCtrl' : IDL.Opt(IDL.Nat),
    'cyclesBurntChallengeGeneration' : IDL.Opt(IDL.Nat),
    'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : IDL.Opt(IDL.Nat),
    'protocolOperationFeesCut' : IDL.Opt(IDL.Nat),
    'dailyChallenges' : IDL.Opt(IDL.Nat),
    'cyclesReinstallMainerllmGsMc' : IDL.Opt(IDL.Nat),
    'dailySubmissionsPerShareMEDIUM' : IDL.Opt(IDL.Nat),
    'cyclesReinstallMainerllmMcMainerllm' : IDL.Opt(IDL.Nat),
    'cyclesBurntResponseGenerationShare' : IDL.Opt(IDL.Nat),
    'numShareServiceLlms' : IDL.Opt(IDL.Nat),
    'cyclesUpgradeMainerctrlGsMc' : IDL.Opt(IDL.Nat),
    'numChallengerLlms' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateJuctrl' : IDL.Opt(IDL.Nat),
    'cyclesGenerateResponseOwnctrlOwnllmHIGH' : IDL.Opt(IDL.Nat),
    'cyclesBurntResponseGenerationOwn' : IDL.Opt(IDL.Nat),
    'dailySubmissionsPerShareLOW' : IDL.Opt(IDL.Nat),
    'cyclesUpgradeMainerctrlMcMainerctrl' : IDL.Opt(IDL.Nat),
    'cyclesGenerateResponseOwnctrlOwnllmLOW' : IDL.Opt(IDL.Nat),
    'costGenerateResponseOwnctrl' : IDL.Opt(IDL.Nat),
    'costGenerateChallengeChctrl' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateSactrl' : IDL.Opt(IDL.Nat),
    'dailySubmissionsPerOwnLOW' : IDL.Opt(IDL.Nat),
    'cyclesGenerateResponseSsctrlSsllm' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateOwnctrl' : IDL.Opt(IDL.Nat),
    'cyclesReinstallMainerctrlMcMainerctrl' : IDL.Opt(IDL.Nat),
    'dailySubmissionsPerOwnMEDIUM' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateChllm' : IDL.Opt(IDL.Nat),
    'cyclesCreateMainerLlmTargetBalance' : IDL.Opt(IDL.Nat),
    'cyclesGenerateResponseOwnctrlGs' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateOwnllm' : IDL.Opt(IDL.Nat),
    'dailySubmissionsPerShareHIGH' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateJullm' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateGs' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateMc' : IDL.Opt(IDL.Nat),
    'marginCost' : IDL.Opt(IDL.Nat),
    'costGenerateResponseShareGs' : IDL.Opt(IDL.Nat),
    'costGenerateChallengeGs' : IDL.Opt(IDL.Nat),
    'costGenerateResponseSactrl' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateSallm' : IDL.Opt(IDL.Nat),
    'cyclesCreatemMainerMarginMc' : IDL.Opt(IDL.Nat),
    'cyclesGenerateChallengeChctrlChllm' : IDL.Opt(IDL.Nat),
    'costGenerateResponseOwnGs' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateSsllm' : IDL.Opt(IDL.Nat),
    'dailySubmissionsPerOwnHIGH' : IDL.Opt(IDL.Nat),
    'costGenerateResponseOwnllm' : IDL.Opt(IDL.Nat),
    'dailySubmissionsAllShare' : IDL.Opt(IDL.Nat),
    'cyclesGenerateScoreGsJuctrl' : IDL.Opt(IDL.Nat),
    'cyclesBurntJudgeScoring' : IDL.Opt(IDL.Nat),
    'cyclesGenerateResponseSactrlSsctrl' : IDL.Opt(IDL.Nat),
    'costGenerateScoreJullm' : IDL.Opt(IDL.Nat),
    'submissionFee' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateSsctrl' : IDL.Opt(IDL.Nat),
    'costUpgradeMainerCtrl' : IDL.Opt(IDL.Nat),
    'costGenerateScoreGs' : IDL.Opt(IDL.Nat),
    'cyclesFailedSubmissionCut' : IDL.Opt(IDL.Nat),
    'costGenerateScoreJuctrl' : IDL.Opt(IDL.Nat),
    'costGenerateChallengeChllm' : IDL.Opt(IDL.Nat),
    'costUpgradeMcMainerLlm' : IDL.Opt(IDL.Nat),
    'costUpgradeMainerLlm' : IDL.Opt(IDL.Nat),
    'dailySubmissionsAllOwn' : IDL.Opt(IDL.Nat),
    'cyclesSubmitResponse' : IDL.Opt(IDL.Nat),
    'cyclesGenerateChallengeGsChctrl' : IDL.Opt(IDL.Nat),
    'cyclesGenerateScoreJuctrlJullm' : IDL.Opt(IDL.Nat),
    'costGenerateResponseSsctrl' : IDL.Opt(IDL.Nat),
    'costGenerateResponseSsllm' : IDL.Opt(IDL.Nat),
    'marginFailedSubmissionCut' : IDL.Opt(IDL.Nat),
    'numJudgeLlms' : IDL.Opt(IDL.Nat),
    'cyclesReinstallMainerctrlGsMc' : IDL.Opt(IDL.Nat),
    'costUpgradeMcMainerCtrl' : IDL.Opt(IDL.Nat),
    'cyclesUpgradeMainerllmGsMc' : IDL.Opt(IDL.Nat),
    'costIdleBurnRateChctrl' : IDL.Opt(IDL.Nat),
    'cyclesGenerateResponseSsctrlGs' : IDL.Opt(IDL.Nat),
    'costCreateMainerLlm' : IDL.Opt(IDL.Nat),
  });
  const MainerLimitInput = IDL.Record({
    'mainerType' : MainerAgentCanisterType,
    'newLimit' : IDL.Nat,
  });
  const UpdateWasmHashInput = IDL.Record({
    'wasmHash' : IDL.Vec(IDL.Nat8),
    'textNote' : IDL.Text,
  });
  const StartUploadJudgePromptCacheRecord = IDL.Record({
    'judgePromptId' : IDL.Text,
  });
  const StartUploadJudgePromptCacheRecordResult = IDL.Variant({
    'Ok' : StartUploadJudgePromptCacheRecord,
    'Err' : ApiError,
  });
  const StartUploadMainerPromptCacheRecord = IDL.Record({
    'mainerPromptId' : IDL.Text,
  });
  const StartUploadMainerPromptCacheRecordResult = IDL.Variant({
    'Ok' : StartUploadMainerPromptCacheRecord,
    'Err' : ApiError,
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
  const ChallengeResponseSubmissionMetadata = IDL.Record({
    'submittedTimestamp' : IDL.Nat64,
    'submissionStatus' : ChallengeResponseSubmissionStatus,
    'cyclesGenerateScoreGsJuctrl' : IDL.Nat,
    'submissionId' : IDL.Text,
    'cyclesGenerateScoreJuctrlJullm' : IDL.Nat,
  });
  const ChallengeResponseSubmissionMetadataResult = IDL.Variant({
    'Ok' : ChallengeResponseSubmissionMetadata,
    'Err' : ApiError,
  });
  const MainerAgentTopUpInput = IDL.Record({
    'paymentTransactionBlockId' : IDL.Nat64,
    'mainerAgent' : OfficialMainerAgentCanister,
  });
  const MainerctrlUpgradeInput = IDL.Record({
    'canisterAddress' : CanisterAddress,
  });
  const UploadJudgePromptCacheBytesChunkInput = IDL.Record({
    'chunkID' : IDL.Nat,
    'bytesChunk' : IDL.Vec(IDL.Nat8),
    'judgePromptId' : IDL.Text,
  });
  const UploadMainerPromptCacheBytesChunkInput = IDL.Record({
    'mainerPromptId' : IDL.Text,
    'chunkID' : IDL.Nat,
    'bytesChunk' : IDL.Vec(IDL.Nat8),
  });
  const WhitelistMainerCreationInput = IDL.Record({
    'status' : CanisterStatus,
    'canisterType' : ProtocolCanisterType,
    'ownedBy' : IDL.Principal,
    'owner' : IDL.Opt(IDL.Principal),
    'creationTimestamp' : IDL.Nat64,
    'createdBy' : IDL.Principal,
    'paymentTransactionBlockId' : IDL.Nat64,
    'mainerConfig' : MainerConfigurationInput,
    'subnet' : IDL.Text,
    'address' : CanisterAddress,
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
    'addCycles' : IDL.Func([], [AddCyclesResult], []),
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
    'archiveSubmissionsAdmin' : IDL.Func([], [NatResult], []),
    'backupMainersAdmin' : IDL.Func([], [NatResult], []),
    'cleanOpenSubmissionsQueueAdmin' : IDL.Func([], [NatResult], []),
    'cleanSubmissionsAdmin' : IDL.Func([], [AuthRecordResult], []),
    'cleanUnlockedMainerStoragesAdmin' : IDL.Func([], [AuthRecordResult], []),
    'completeMainerSetupForUserAdmin' : IDL.Func(
        [OfficialMainerAgentCanister],
        [MainerAgentCanisterResult],
        [],
      ),
    'confirmUserMarketplaceMainerReservation' : IDL.Func(
        [MainerMarketplaceReservationInput],
        [MainerMarketplaceReservationResult],
        ['query'],
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
    'disburseIcpToTreasuryAdmin' : IDL.Func([], [AuthRecordResult], []),
    'downloadJudgePromptCacheBytesChunk' : IDL.Func(
        [DownloadJudgePromptCacheBytesChunkInput],
        [DownloadJudgePromptCacheBytesChunkRecordResult],
        ['query'],
      ),
    'downloadMainerPromptCacheBytesChunk' : IDL.Func(
        [DownloadMainerPromptCacheBytesChunkInput],
        [DownloadMainerPromptCacheBytesChunkRecordResult],
        ['query'],
      ),
    'finishUploadJudgePromptCache' : IDL.Func(
        [FinishUploadJudgePromptCacheInput],
        [StatusCodeRecordResult],
        [],
      ),
    'finishUploadMainerPromptCache' : IDL.Func(
        [FinishUploadMainerPromptCacheInput],
        [StatusCodeRecordResult],
        [],
      ),
    'getArchivedChallengesAdmin' : IDL.Func([], [ChallengesResult], ['query']),
    'getAvailableMainers' : IDL.Func([], [NatResult], ['query']),
    'getBufferMainerCreation' : IDL.Func([], [NatResult], ['query']),
    'getCanisterPrincipal' : IDL.Func([], [IDL.Text], ['query']),
    'getClosedChallengesAdmin' : IDL.Func([], [ChallengesResult], ['query']),
    'getCurrentChallenges' : IDL.Func([], [ChallengesResult], ['query']),
    'getCurrentChallengesAdmin' : IDL.Func([], [ChallengesResult], ['query']),
    'getCyclesBalanceThresholdFunnaiTopups' : IDL.Func(
        [],
        [NatResult],
        ['query'],
      ),
    'getCyclesBurnRate' : IDL.Func(
        [CyclesBurnRateDefault],
        [CyclesBurnRateResult],
        [],
      ),
    'getCyclesFlowAdmin' : IDL.Func([], [CyclesFlowResult], []),
    'getCyclesTransactionsAdmin' : IDL.Func(
        [],
        [CyclesTransactionsResult],
        ['query'],
      ),
    'getDisburseFundsToTreasuryFlag' : IDL.Func([], [FlagResult], ['query']),
    'getFunnaiCyclesPrice' : IDL.Func([], [NatResult], ['query']),
    'getFunnaiCyclesPriceAdmin' : IDL.Func([], [NatResult], ['query']),
    'getGameStateThresholdsAdmin' : IDL.Func(
        [],
        [GameStateTresholdsResult],
        ['query'],
      ),
    'getIsMainerAuctionActive' : IDL.Func([], [FlagResult], ['query']),
    'getIsMigratingChallengesFlagAdmin' : IDL.Func([], [FlagResult], ['query']),
    'getIsWhitelistPhaseActive' : IDL.Func([], [FlagResult], ['query']),
    'getJudgePromptInfo' : IDL.Func(
        [IDL.Text],
        [JudgePromptInfoResult],
        ['query'],
      ),
    'getLimitForCreatingMainerAdmin' : IDL.Func(
        [CheckMainerLimit],
        [NatResult],
        ['query'],
      ),
    'getMainerAgentCanisterInfo' : IDL.Func(
        [CanisterRetrieveInput],
        [MainerAgentCanisterResult],
        ['query'],
      ),
    'getMainerAgentCanistersAdmin' : IDL.Func(
        [],
        [MainerAgentCanistersResult],
        ['query'],
      ),
    'getMainerAgentCanistersForUser' : IDL.Func(
        [],
        [MainerAgentCanistersResult],
        ['query'],
      ),
    'getMainerAgentCanistersForUserAdmin' : IDL.Func(
        [IDL.Text],
        [MainerAgentCanistersResult],
        ['query'],
      ),
    'getMainerAuctionTimerInfo' : IDL.Func(
        [],
        [MainerAuctionTimerInfoResult],
        ['query'],
      ),
    'getMainerCyclesUsedPerResponse' : IDL.Func([], [NatResult], []),
    'getMainerPromptInfo' : IDL.Func(
        [IDL.Text],
        [MainerPromptInfoResult],
        ['query'],
      ),
    'getMarketplaceMainerListings' : IDL.Func(
        [],
        [MainerMarketplaceListingsResult],
        ['query'],
      ),
    'getMaxFunnaiTopupCyclesAmount' : IDL.Func([], [NatResult], ['query']),
    'getMaxFunnaiTopupCyclesAmountAdmin' : IDL.Func([], [NatResult], ['query']),
    'getMinimumIcpBalance' : IDL.Func([], [NatResult], ['query']),
    'getNextMainerAuctionPriceDropAtNs' : IDL.Func([], [NatResult], ['query']),
    'getNextSubmissionToJudge' : IDL.Func(
        [],
        [ChallengeResponseSubmissionWithQueueStatusResult],
        [],
      ),
    'getNumArchivedChallengesAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumArchivedSubmissionsAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumClosedChallengesAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumCurrentChallengesAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumMainerAgentCanistersForUserAdmin' : IDL.Func(
        [IDL.Text],
        [NatResult],
        ['query'],
      ),
    'getNumOpenSubmissionsAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumOpenSubmissionsForOpenChallengesAdmin' : IDL.Func(
        [],
        [NatResult],
        ['query'],
      ),
    'getNumScoredChallengesAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumSubmissionsAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumSubmissionsToMigrateAdmin' : IDL.Func([], [NatResult], ['query']),
    'getNumberMainerAgentsAdmin' : IDL.Func(
        [CheckMainerLimit],
        [NatResult],
        ['query'],
      ),
    'getOfficialCanistersAdmin' : IDL.Func(
        [],
        [IDL.Vec(OfficialProtocolCanister)],
        ['query'],
      ),
    'getOfficialChallengerCanisters' : IDL.Func([], [AuthRecordResult], []),
    'getOpenSubmissionsAdmin' : IDL.Func(
        [],
        [ChallengeResponseSubmissionsResult],
        ['query'],
      ),
    'getOpenSubmissionsForOpenChallengesAdmin' : IDL.Func(
        [],
        [ChallengeResponseSubmissionsResult],
        ['query'],
      ),
    'getOpenSubmissionsQueueSizeAdmin' : IDL.Func([], [NatResult], ['query']),
    'getPauseProtocolFlag' : IDL.Func([], [FlagResult], ['query']),
    'getPauseWhitelistMainerCreationFlag' : IDL.Func(
        [],
        [FlagResult],
        ['query'],
      ),
    'getPriceForOwnMainer' : IDL.Func([], [PriceResult], ['query']),
    'getPriceForShareAgent' : IDL.Func([], [PriceResult], ['query']),
    'getProtocolCyclesBalanceBuffer' : IDL.Func([], [NatResult], ['query']),
    'getProtocolTotalCyclesBurnt' : IDL.Func(
        [],
        [CyclesBurntResult],
        ['query'],
      ),
    'getRandomOpenChallenge' : IDL.Func([], [ChallengeResult], []),
    'getRandomOpenChallengeAdmin' : IDL.Func([], [ChallengeResult], []),
    'getRandomOpenChallengeTopic' : IDL.Func([], [ChallengeTopicResult], []),
    'getRandomOpenChallengeTopicAdmin' : IDL.Func(
        [],
        [ChallengeTopicResult],
        [],
      ),
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
    'getRedeemedFunnaiTransactionBlockAdmin' : IDL.Func(
        [PaymentTransactionBlockId],
        [RedeemedTransactionBlockResult],
        [],
      ),
    'getRedeemedFunnaiTransactionBlocksAdmin' : IDL.Func(
        [],
        [RedeemedTransactionBlocksResult],
        [],
      ),
    'getRedeemedTransactionBlockAdmin' : IDL.Func(
        [PaymentTransactionBlockId],
        [RedeemedTransactionBlockResult],
        [],
      ),
    'getRedeemedTransactionBlocksAdmin' : IDL.Func(
        [],
        [RedeemedTransactionBlocksResult],
        [],
      ),
    'getRewardPerChallengeAdmin' : IDL.Func([], [RewardPerChallengeResult], []),
    'getRoundRobinChallengeIndexAdmin' : IDL.Func([], [NatResult], ['query']),
    'getRoundRobinTopicIndexAdmin' : IDL.Func([], [NatResult], ['query']),
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
    'getSharedServiceCanistersAdmin' : IDL.Func(
        [],
        [OfficialProtocolCanistersResult],
        [],
      ),
    'getSubmissionsAdmin' : IDL.Func(
        [],
        [ChallengeResponseSubmissionsResult],
        ['query'],
      ),
    'getSubnetsAdmin' : IDL.Func([], [SubnetIdsResult], ['query']),
    'getTreasuryCanisterId' : IDL.Func([], [IDL.Text], ['query']),
    'getUserMarketplaceMainerListings' : IDL.Func(
        [],
        [MainerMarketplaceListingsResult],
        ['query'],
      ),
    'getWhitelistPriceForOwnMainer' : IDL.Func([], [PriceResult], ['query']),
    'getWhitelistPriceForShareAgent' : IDL.Func([], [PriceResult], ['query']),
    'health' : IDL.Func([], [StatusCodeRecordResult], ['query']),
    'icrc10_supported_standards' : IDL.Func(
        [],
        [SupportedStandards],
        ['query'],
      ),
    'icrc37_approve_tokens' : IDL.Func(
        [IDL.Vec(ApproveTokenArg)],
        [IDL.Vec(IDL.Opt(ApproveTokenResult))],
        [],
      ),
    'icrc37_revoke_token_approvals' : IDL.Func(
        [IDL.Vec(RevokeTokenApprovalArg)],
        [IDL.Vec(IDL.Opt(RevokeTokenApprovalResult))],
        [],
      ),
    'icrc37_transfer_from' : IDL.Func(
        [IDL.Vec(TransferFromArg)],
        [IDL.Vec(IDL.Opt(TransferFromResult))],
        [],
      ),
    'icrc7_balance_of' : IDL.Func(
        [IDL.Vec(Account)],
        [IDL.Vec(IDL.Nat)],
        ['query'],
      ),
    'icrc7_collection_metadata' : IDL.Func(
        [],
        [IDL.Vec(IDL.Tuple(IDL.Text, Value))],
        ['query'],
      ),
    'icrc7_description' : IDL.Func([], [IDL.Opt(IDL.Text)], ['query']),
    'icrc7_logo' : IDL.Func([], [IDL.Opt(IDL.Text)], ['query']),
    'icrc7_name' : IDL.Func([], [IDL.Text], ['query']),
    'icrc7_supply_cap' : IDL.Func([], [IDL.Opt(IDL.Nat)], ['query']),
    'icrc7_symbol' : IDL.Func([], [IDL.Text], ['query']),
    'icrc7_token_metadata' : IDL.Func(
        [IDL.Vec(IDL.Nat)],
        [IDL.Vec(IDL.Opt(IDL.Vec(IDL.Tuple(IDL.Text, Value))))],
        ['query'],
      ),
    'icrc7_tokens' : IDL.Func(
        [IDL.Opt(IDL.Nat), IDL.Opt(IDL.Nat)],
        [IDL.Vec(IDL.Nat)],
        ['query'],
      ),
    'icrc7_total_supply' : IDL.Func([], [IDL.Nat], ['query']),
    'initializeOpenSubmissionsQueueAdmin' : IDL.Func(
        [],
        [AuthRecordResult],
        [],
      ),
    'migrateArchivedChallengesAdmin' : IDL.Func([], [NatResult], []),
    'migrateScoredResponsesForChallengeAdmin' : IDL.Func(
        [IDL.Text],
        [AuthRecordResult],
        [],
      ),
    'migrateSubmissionsAdmin' : IDL.Func([], [AuthRecordResult], []),
    'migrateWinnerDeclarationsAdmin' : IDL.Func(
        [IDL.Vec(IDL.Text)],
        [AuthRecordResult],
        [],
      ),
    'reinstallMainerControllerAdmin' : IDL.Func(
        [MainerctrlReinstallInput],
        [MainerAgentCanisterResult],
        [],
      ),
    'removeRedeemedFunnaiTransactionBlockAdmin' : IDL.Func(
        [PaymentTransactionBlockId],
        [TextResult],
        [],
      ),
    'removeRedeemedTransactionBlockAdmin' : IDL.Func(
        [PaymentTransactionBlockId],
        [TextResult],
        [],
      ),
    'removeSharedServiceCanisterAdmin' : IDL.Func(
        [IDL.Record({ 'canisterId' : IDL.Text })],
        [StatusCodeRecordResult],
        [],
      ),
    'reserveMarketplaceListedMainer' : IDL.Func(
        [MainerMarketplaceReservationInput],
        [MainerMarketplaceReservationResult],
        [],
      ),
    'resetCurrentChallengesAdmin' : IDL.Func([], [StatusCodeRecordResult], []),
    'resetCyclesFlowAdmin' : IDL.Func([], [StatusCodeRecordResult], []),
    'resetIsMigratingChallengesFlagAdmin' : IDL.Func(
        [],
        [AuthRecordResult],
        [],
      ),
    'resetRoundRobinChallengeIndexAdmin' : IDL.Func(
        [],
        [StatusCodeRecordResult],
        [],
      ),
    'resetRoundRobinTopicIndexAdmin' : IDL.Func(
        [],
        [StatusCodeRecordResult],
        [],
      ),
    'setApiCanisterId' : IDL.Func([IDL.Text], [AuthRecordResult], []),
    'setArchiveCanisterId' : IDL.Func([IDL.Text], [AuthRecordResult], []),
    'setAuctionIntervalSecondsAdmin' : IDL.Func(
        [IDL.Nat],
        [AuthRecordResult],
        [],
      ),
    'setAuctionPricesAdmin' : IDL.Func(
        [IDL.Vec(IDL.Nat64)],
        [AuthRecordResult],
        [],
      ),
    'setBufferMainerCreation' : IDL.Func([IDL.Nat], [AuthRecordResult], []),
    'setCyclesBalanceThresholdFunnaiTopups' : IDL.Func(
        [IDL.Nat],
        [AuthRecordResult],
        [],
      ),
    'setCyclesBurnRateAdmin' : IDL.Func(
        [SetCyclesBurnRateInput],
        [StatusCodeRecordResult],
        [],
      ),
    'setCyclesFlowAdmin' : IDL.Func(
        [CyclesFlowSettings],
        [StatusCodeRecordResult],
        [],
      ),
    'setFunnaiCyclesPrice' : IDL.Func([IDL.Nat], [AuthRecordResult], []),
    'setGameStateThresholdsAdmin' : IDL.Func(
        [GameStateTresholds],
        [StatusCodeRecordResult],
        [],
      ),
    'setIcpForOwnMainerAdmin' : IDL.Func(
        [IDL.Nat64],
        [StatusCodeRecordResult],
        [],
      ),
    'setIcpForShareAgentAdmin' : IDL.Func(
        [IDL.Nat64],
        [StatusCodeRecordResult],
        [],
      ),
    'setIcpForWhitelistOwnMainerAdmin' : IDL.Func(
        [IDL.Nat64],
        [StatusCodeRecordResult],
        [],
      ),
    'setIcpForWhitelistShareAgentAdmin' : IDL.Func(
        [IDL.Nat64],
        [StatusCodeRecordResult],
        [],
      ),
    'setInitialChallengeTopics' : IDL.Func([], [StatusCodeRecordResult], []),
    'setLimitForCreatingMainerAdmin' : IDL.Func(
        [MainerLimitInput],
        [AuthRecordResult],
        [],
      ),
    'setMaxFunnaiTopupCyclesAmount' : IDL.Func(
        [IDL.Nat],
        [AuthRecordResult],
        [],
      ),
    'setMinimumIcpBalance' : IDL.Func([IDL.Nat], [AuthRecordResult], []),
    'setNumSubmissionsToMigrateAdmin' : IDL.Func([IDL.Nat], [NatResult], []),
    'setOfficialMainerAgentCanisterWasmHashAdmin' : IDL.Func(
        [UpdateWasmHashInput],
        [CanisterWasmHashRecordResult],
        [],
      ),
    'setProtocolCyclesBalanceBuffer' : IDL.Func(
        [IDL.Nat],
        [AuthRecordResult],
        [],
      ),
    'setRewardPerChallengeAdmin' : IDL.Func(
        [IDL.Nat],
        [RewardPerChallengeResult],
        [],
      ),
    'setSubnetsAdmin' : IDL.Func([SubnetIds], [StatusCodeRecordResult], []),
    'setTokenLedgerCanisterId' : IDL.Func([IDL.Text], [AuthRecordResult], []),
    'setTreasuryCanisterId' : IDL.Func([IDL.Text], [AuthRecordResult], []),
    'setUpMainerLlmCanister' : IDL.Func(
        [OfficialMainerAgentCanister],
        [SetUpMainerLlmCanisterResult],
        [],
      ),
    'setupAuctionAdmin' : IDL.Func(
        [IDL.Vec(IDL.Nat64), IDL.Nat],
        [AuthRecordResult],
        [],
      ),
    'shouldCreatingMainersBeStopped' : IDL.Func(
        [CheckMainerLimit],
        [FlagResult],
        ['query'],
      ),
    'spinUpMainerControllerCanister' : IDL.Func(
        [OfficialMainerAgentCanister],
        [MainerAgentCanisterResult],
        [],
      ),
    'spinUpMainerControllerCanisterForUserAdmin' : IDL.Func(
        [OfficialMainerAgentCanister],
        [MainerAgentCanisterResult],
        [],
      ),
    'startAuctionAdmin' : IDL.Func([], [AuthRecordResult], []),
    'startUploadJudgePromptCache' : IDL.Func(
        [],
        [StartUploadJudgePromptCacheRecordResult],
        [],
      ),
    'startUploadMainerPromptCache' : IDL.Func(
        [],
        [StartUploadMainerPromptCacheRecordResult],
        [],
      ),
    'stopAuctionAdmin' : IDL.Func([], [AuthRecordResult], []),
    'submitChallengeResponse' : IDL.Func(
        [ChallengeResponseSubmissionInput],
        [ChallengeResponseSubmissionMetadataResult],
        [],
      ),
    'testDisbursementToTreasuryAdmin' : IDL.Func([], [AuthRecordResult], []),
    'testMainerCodeIntegrityAdmin' : IDL.Func([], [AuthRecordResult], []),
    'testTokenMintingAdmin' : IDL.Func([], [AuthRecordResult], []),
    'toggleDisburseFundsToTreasuryFlagAdmin' : IDL.Func(
        [],
        [AuthRecordResult],
        [],
      ),
    'togglePauseProtocolFlagAdmin' : IDL.Func([], [AuthRecordResult], []),
    'togglePauseWhitelistMainerCreationFlagAdmin' : IDL.Func(
        [],
        [AuthRecordResult],
        [],
      ),
    'toggleWhitelistPhaseActiveFlagAdmin' : IDL.Func(
        [],
        [AuthRecordResult],
        [],
      ),
    'topUpCyclesForMainerAgent' : IDL.Func(
        [MainerAgentTopUpInput],
        [MainerAgentCanisterResult],
        [],
      ),
    'topUpCyclesForMainerAgentWithFunnai' : IDL.Func(
        [MainerAgentTopUpInput],
        [MainerAgentCanisterResult],
        [],
      ),
    'unlockUserMainerAgent' : IDL.Func(
        [MainerCreationInput],
        [MainerAgentCanisterResult],
        [],
      ),
    'upgradeMainerControllerAdmin' : IDL.Func(
        [MainerctrlUpgradeInput],
        [MainerAgentCanisterResult],
        [],
      ),
    'uploadJudgePromptCacheBytesChunk' : IDL.Func(
        [UploadJudgePromptCacheBytesChunkInput],
        [StatusCodeRecordResult],
        [],
      ),
    'uploadMainerPromptCacheBytesChunk' : IDL.Func(
        [UploadMainerPromptCacheBytesChunkInput],
        [StatusCodeRecordResult],
        [],
      ),
    'whitelistCreateUserMainerAgent' : IDL.Func(
        [WhitelistMainerCreationInput],
        [MainerAgentCanisterResult],
        [],
      ),
  });
  return GameStateCanister;
};
export const init = ({ IDL }) => { return []; };
