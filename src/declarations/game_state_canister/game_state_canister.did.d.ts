import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export type ApiError = { 'FailedOperation' : null } |
  { 'InvalidId' : null } |
  { 'ZeroAddress' : null } |
  { 'Unauthorized' : null } |
  { 'StatusCode' : StatusCode } |
  { 'Other' : string } |
  { 'InsuffientCycles' : bigint };
export interface AuthRecord { 'auth' : string }
export type AuthRecordResult = { 'Ok' : AuthRecord } |
  { 'Err' : ApiError };
export type CanisterAddress = string;
export interface CanisterInput {
  'canisterType' : ProtocolCanisterType,
  'subnet' : string,
  'address' : CanisterAddress,
}
export interface CanisterRetrieveInput { 'address' : CanisterAddress }
export type CanisterStatus = { 'Paused' : null } |
  { 'Paid' : null } |
  { 'Unlocked' : null } |
  { 'LlmSetupFinished' : null } |
  { 'ControllerCreated' : null } |
  { 'LlmSetupInProgress' : LlmSetupStatus } |
  { 'Running' : null } |
  { 'Other' : string } |
  { 'ControllerCreationInProgress' : null };
export interface CanisterWasmHashRecord {
  'creationTimestamp' : bigint,
  'wasmHash' : Uint8Array | number[],
  'createdBy' : Principal,
  'textNote' : string,
  'version' : bigint,
}
export type CanisterWasmHashRecordResult = { 'Ok' : CanisterWasmHashRecord } |
  { 'Err' : ApiError };
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
export type ChallengeAdditionResult = { 'Ok' : Challenge } |
  { 'Err' : ApiError };
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
export interface ChallengeResponseSubmission {
  'challengeClosedTimestamp' : [] | [bigint],
  'challengeTopicStatus' : ChallengeTopicStatus,
  'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : bigint,
  'protocolOperationFeesCut' : bigint,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeCreationTimestamp' : bigint,
  'challengeCreatedBy' : CanisterAddress,
  'challengeTopicId' : string,
  'cyclesGenerateResponseOwnctrlOwnllmHIGH' : bigint,
  'submittedTimestamp' : bigint,
  'cyclesGenerateResponseOwnctrlOwnllmLOW' : bigint,
  'mainerPromptId' : string,
  'cyclesGenerateResponseSsctrlSsllm' : bigint,
  'mainerMaxContinueLoopCount' : bigint,
  'submittedBy' : Principal,
  'mainerTemp' : number,
  'challengeStatus' : ChallengeStatus,
  'cyclesGenerateResponseOwnctrlGs' : bigint,
  'challengeQuestionSeed' : number,
  'mainerNumTokens' : bigint,
  'submissionStatus' : ChallengeResponseSubmissionStatus,
  'challengeQuestion' : string,
  'challengeId' : string,
  'challengeQueuedBy' : Principal,
  'challengeQueuedId' : string,
  'challengeQueuedTo' : Principal,
  'challengeTopic' : string,
  'cyclesGenerateChallengeChctrlChllm' : bigint,
  'cyclesGenerateScoreGsJuctrl' : bigint,
  'cyclesGenerateResponseSactrlSsctrl' : bigint,
  'judgePromptId' : string,
  'submissionId' : string,
  'challengeAnswerSeed' : number,
  'challengeAnswer' : string,
  'challengeQueuedTimestamp' : bigint,
  'cyclesSubmitResponse' : bigint,
  'cyclesGenerateChallengeGsChctrl' : bigint,
  'cyclesGenerateScoreJuctrlJullm' : bigint,
  'cyclesGenerateResponseSsctrlGs' : bigint,
}
export interface ChallengeResponseSubmissionInput {
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
  'submittedBy' : Principal,
  'mainerTemp' : number,
  'challengeStatus' : ChallengeStatus,
  'cyclesGenerateResponseOwnctrlGs' : bigint,
  'challengeQuestionSeed' : number,
  'mainerNumTokens' : bigint,
  'challengeQuestion' : string,
  'challengeId' : string,
  'challengeQueuedBy' : Principal,
  'challengeQueuedId' : string,
  'challengeQueuedTo' : Principal,
  'challengeTopic' : string,
  'cyclesGenerateChallengeChctrlChllm' : bigint,
  'cyclesGenerateResponseSactrlSsctrl' : bigint,
  'judgePromptId' : string,
  'challengeAnswerSeed' : number,
  'challengeAnswer' : string,
  'challengeQueuedTimestamp' : bigint,
  'cyclesSubmitResponse' : bigint,
  'cyclesGenerateChallengeGsChctrl' : bigint,
  'cyclesGenerateResponseSsctrlGs' : bigint,
}
export interface ChallengeResponseSubmissionMetadata {
  'submittedTimestamp' : bigint,
  'submissionStatus' : ChallengeResponseSubmissionStatus,
  'cyclesGenerateScoreGsJuctrl' : bigint,
  'submissionId' : string,
  'cyclesGenerateScoreJuctrlJullm' : bigint,
}
export type ChallengeResponseSubmissionMetadataResult = {
    'Ok' : ChallengeResponseSubmissionMetadata
  } |
  { 'Err' : ApiError };
export type ChallengeResponseSubmissionResult = {
    'Ok' : ChallengeResponseSubmission
  } |
  { 'Err' : ApiError };
export type ChallengeResponseSubmissionStatus = { 'Judged' : null } |
  { 'FailedSubmission' : null } |
  { 'Processed' : null } |
  { 'Judging' : null } |
  { 'Received' : null } |
  { 'Other' : string } |
  { 'Submitted' : null };
export type ChallengeResponseSubmissionsResult = {
    'Ok' : Array<ChallengeResponseSubmission>
  } |
  { 'Err' : ApiError };
export type ChallengeResult = { 'Ok' : Challenge } |
  { 'Err' : ApiError };
export type ChallengeStatus = { 'Open' : null } |
  { 'Closed' : null } |
  { 'Archived' : null } |
  { 'Other' : string };
export interface ChallengeTopic {
  'challengeTopicStatus' : ChallengeTopicStatus,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeTopicId' : string,
  'challengeTopic' : string,
  'cyclesGenerateChallengeChctrlChllm' : bigint,
  'cyclesGenerateChallengeGsChctrl' : bigint,
}
export interface ChallengeTopicInput { 'challengeTopic' : string }
export type ChallengeTopicResult = { 'Ok' : ChallengeTopic } |
  { 'Err' : ApiError };
export type ChallengeTopicStatus = { 'Open' : null } |
  { 'Closed' : null } |
  { 'Archived' : null } |
  { 'Other' : string };
export interface ChallengeWinnerDeclaration {
  'participants' : List_1,
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
export type ChallengeWinnersResult = {
    'Ok' : Array<ChallengeWinnerDeclaration>
  } |
  { 'Err' : ApiError };
export type ChallengesResult = { 'Ok' : Array<Challenge> } |
  { 'Err' : ApiError };
export interface CheckMainerLimit { 'mainerType' : MainerAgentCanisterType }
export interface CyclesBurnRate {
  'cycles' : bigint,
  'timeInterval' : TimeInterval,
}
export type CyclesBurnRateDefault = { 'Low' : null } |
  { 'Mid' : null } |
  { 'VeryHigh' : null } |
  { 'High' : null } |
  { 'Custom' : CyclesBurnRate };
export type CyclesBurnRateResult = { 'Ok' : CyclesBurnRate } |
  { 'Err' : ApiError };
export type CyclesBurntResult = { 'Ok' : bigint } |
  { 'Err' : ApiError };
export interface CyclesFlow {
  'costCreateMcMainerLlm' : bigint,
  'cyclesCreateMainerMarginGs' : bigint,
  'costCreateMainerCtrl' : bigint,
  'costCreateMcMainerCtrl' : bigint,
  'cyclesBurntChallengeGeneration' : bigint,
  'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : bigint,
  'protocolOperationFeesCut' : bigint,
  'dailyChallenges' : bigint,
  'dailySubmissionsPerShareMEDIUM' : bigint,
  'cyclesBurntResponseGenerationShare' : bigint,
  'numShareServiceLlms' : bigint,
  'numChallengerLlms' : bigint,
  'costIdleBurnRateJuctrl' : bigint,
  'cyclesGenerateResponseOwnctrlOwnllmHIGH' : bigint,
  'cyclesBurntResponseGenerationOwn' : bigint,
  'dailySubmissionsPerShareLOW' : bigint,
  'cyclesGenerateResponseOwnctrlOwnllmLOW' : bigint,
  'costGenerateResponseOwnctrl' : bigint,
  'costGenerateChallengeChctrl' : bigint,
  'costIdleBurnRateSactrl' : bigint,
  'dailySubmissionsPerOwnLOW' : bigint,
  'cyclesGenerateResponseSsctrlSsllm' : bigint,
  'costIdleBurnRateOwnctrl' : bigint,
  'dailySubmissionsPerOwnMEDIUM' : bigint,
  'costIdleBurnRateChllm' : bigint,
  'cyclesCreateMainerLlmTargetBalance' : bigint,
  'cyclesGenerateResponseOwnctrlGs' : bigint,
  'costIdleBurnRateOwnllm' : bigint,
  'dailySubmissionsPerShareHIGH' : bigint,
  'costIdleBurnRateJullm' : bigint,
  'costIdleBurnRateGs' : bigint,
  'costIdleBurnRateMc' : bigint,
  'marginCost' : bigint,
  'costGenerateResponseShareGs' : bigint,
  'costGenerateChallengeGs' : bigint,
  'costGenerateResponseSactrl' : bigint,
  'costIdleBurnRateSallm' : bigint,
  'cyclesCreatemMainerMarginMc' : bigint,
  'cyclesGenerateChallengeChctrlChllm' : bigint,
  'costGenerateResponseOwnGs' : bigint,
  'costIdleBurnRateSsllm' : bigint,
  'dailySubmissionsPerOwnHIGH' : bigint,
  'costGenerateResponseOwnllm' : bigint,
  'dailySubmissionsAllShare' : bigint,
  'cyclesGenerateScoreGsJuctrl' : bigint,
  'cyclesBurntJudgeScoring' : bigint,
  'cyclesGenerateResponseSactrlSsctrl' : bigint,
  'costGenerateScoreJullm' : bigint,
  'submissionFee' : bigint,
  'costIdleBurnRateSsctrl' : bigint,
  'costUpgradeMainerCtrl' : bigint,
  'costGenerateScoreGs' : bigint,
  'cyclesFailedSubmissionCut' : bigint,
  'costGenerateScoreJuctrl' : bigint,
  'costGenerateChallengeChllm' : bigint,
  'costUpgradeMcMainerLlm' : bigint,
  'costUpgradeMainerLlm' : bigint,
  'dailySubmissionsAllOwn' : bigint,
  'cyclesSubmitResponse' : bigint,
  'cyclesGenerateChallengeGsChctrl' : bigint,
  'cyclesGenerateScoreJuctrlJullm' : bigint,
  'costGenerateResponseSsctrl' : bigint,
  'costGenerateResponseSsllm' : bigint,
  'marginFailedSubmissionCut' : bigint,
  'numJudgeLlms' : bigint,
  'costUpgradeMcMainerCtrl' : bigint,
  'costIdleBurnRateChctrl' : bigint,
  'cyclesGenerateResponseSsctrlGs' : bigint,
  'costCreateMainerLlm' : bigint,
}
export type CyclesFlowResult = { 'Ok' : CyclesFlow } |
  { 'Err' : ApiError };
export interface CyclesFlowSettings {
  'costCreateMcMainerLlm' : [] | [bigint],
  'cyclesCreateMainerMarginGs' : [] | [bigint],
  'costCreateMainerCtrl' : [] | [bigint],
  'cyclesUpgradeMainerllmMcMainerllm' : [] | [bigint],
  'costCreateMcMainerCtrl' : [] | [bigint],
  'cyclesBurntChallengeGeneration' : [] | [bigint],
  'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : [] | [bigint],
  'protocolOperationFeesCut' : [] | [bigint],
  'dailyChallenges' : [] | [bigint],
  'cyclesReinstallMainerllmGsMc' : [] | [bigint],
  'dailySubmissionsPerShareMEDIUM' : [] | [bigint],
  'cyclesReinstallMainerllmMcMainerllm' : [] | [bigint],
  'cyclesBurntResponseGenerationShare' : [] | [bigint],
  'numShareServiceLlms' : [] | [bigint],
  'cyclesUpgradeMainerctrlGsMc' : [] | [bigint],
  'numChallengerLlms' : [] | [bigint],
  'costIdleBurnRateJuctrl' : [] | [bigint],
  'cyclesGenerateResponseOwnctrlOwnllmHIGH' : [] | [bigint],
  'cyclesBurntResponseGenerationOwn' : [] | [bigint],
  'dailySubmissionsPerShareLOW' : [] | [bigint],
  'cyclesUpgradeMainerctrlMcMainerctrl' : [] | [bigint],
  'cyclesGenerateResponseOwnctrlOwnllmLOW' : [] | [bigint],
  'costGenerateResponseOwnctrl' : [] | [bigint],
  'costGenerateChallengeChctrl' : [] | [bigint],
  'costIdleBurnRateSactrl' : [] | [bigint],
  'dailySubmissionsPerOwnLOW' : [] | [bigint],
  'cyclesGenerateResponseSsctrlSsllm' : [] | [bigint],
  'costIdleBurnRateOwnctrl' : [] | [bigint],
  'cyclesReinstallMainerctrlMcMainerctrl' : [] | [bigint],
  'dailySubmissionsPerOwnMEDIUM' : [] | [bigint],
  'costIdleBurnRateChllm' : [] | [bigint],
  'cyclesCreateMainerLlmTargetBalance' : [] | [bigint],
  'cyclesGenerateResponseOwnctrlGs' : [] | [bigint],
  'costIdleBurnRateOwnllm' : [] | [bigint],
  'dailySubmissionsPerShareHIGH' : [] | [bigint],
  'costIdleBurnRateJullm' : [] | [bigint],
  'costIdleBurnRateGs' : [] | [bigint],
  'costIdleBurnRateMc' : [] | [bigint],
  'marginCost' : [] | [bigint],
  'costGenerateResponseShareGs' : [] | [bigint],
  'costGenerateChallengeGs' : [] | [bigint],
  'costGenerateResponseSactrl' : [] | [bigint],
  'costIdleBurnRateSallm' : [] | [bigint],
  'cyclesCreatemMainerMarginMc' : [] | [bigint],
  'cyclesGenerateChallengeChctrlChllm' : [] | [bigint],
  'costGenerateResponseOwnGs' : [] | [bigint],
  'costIdleBurnRateSsllm' : [] | [bigint],
  'dailySubmissionsPerOwnHIGH' : [] | [bigint],
  'costGenerateResponseOwnllm' : [] | [bigint],
  'dailySubmissionsAllShare' : [] | [bigint],
  'cyclesGenerateScoreGsJuctrl' : [] | [bigint],
  'cyclesBurntJudgeScoring' : [] | [bigint],
  'cyclesGenerateResponseSactrlSsctrl' : [] | [bigint],
  'costGenerateScoreJullm' : [] | [bigint],
  'submissionFee' : [] | [bigint],
  'costIdleBurnRateSsctrl' : [] | [bigint],
  'costUpgradeMainerCtrl' : [] | [bigint],
  'costGenerateScoreGs' : [] | [bigint],
  'cyclesFailedSubmissionCut' : [] | [bigint],
  'costGenerateScoreJuctrl' : [] | [bigint],
  'costGenerateChallengeChllm' : [] | [bigint],
  'costUpgradeMcMainerLlm' : [] | [bigint],
  'costUpgradeMainerLlm' : [] | [bigint],
  'dailySubmissionsAllOwn' : [] | [bigint],
  'cyclesSubmitResponse' : [] | [bigint],
  'cyclesGenerateChallengeGsChctrl' : [] | [bigint],
  'cyclesGenerateScoreJuctrlJullm' : [] | [bigint],
  'costGenerateResponseSsctrl' : [] | [bigint],
  'costGenerateResponseSsllm' : [] | [bigint],
  'marginFailedSubmissionCut' : [] | [bigint],
  'numJudgeLlms' : [] | [bigint],
  'cyclesReinstallMainerctrlGsMc' : [] | [bigint],
  'costUpgradeMcMainerCtrl' : [] | [bigint],
  'cyclesUpgradeMainerllmGsMc' : [] | [bigint],
  'costIdleBurnRateChctrl' : [] | [bigint],
  'cyclesGenerateResponseSsctrlGs' : [] | [bigint],
  'costCreateMainerLlm' : [] | [bigint],
}
export interface DeriveWasmHashInput {
  'textNote' : string,
  'address' : CanisterAddress,
}
export interface DownloadJudgePromptCacheBytesChunkInput {
  'chunkID' : bigint,
  'judgePromptId' : string,
}
export interface DownloadJudgePromptCacheBytesChunkRecord {
  'chunkID' : bigint,
  'bytesChunk' : Uint8Array | number[],
  'judgePromptId' : string,
}
export type DownloadJudgePromptCacheBytesChunkRecordResult = {
    'Ok' : DownloadJudgePromptCacheBytesChunkRecord
  } |
  { 'Err' : ApiError };
export interface DownloadMainerPromptCacheBytesChunkInput {
  'mainerPromptId' : string,
  'chunkID' : bigint,
}
export interface DownloadMainerPromptCacheBytesChunkRecord {
  'mainerPromptId' : string,
  'chunkID' : bigint,
  'bytesChunk' : Uint8Array | number[],
}
export type DownloadMainerPromptCacheBytesChunkRecordResult = {
    'Ok' : DownloadMainerPromptCacheBytesChunkRecord
  } |
  { 'Err' : ApiError };
export interface FinishUploadJudgePromptCacheInput {
  'promptCacheFilename' : string,
  'promptText' : string,
  'judgePromptId' : string,
  'promptCacheSha256' : string,
}
export interface FinishUploadMainerPromptCacheInput {
  'promptCacheFilename' : string,
  'mainerPromptId' : string,
  'promptText' : string,
  'promptCacheSha256' : string,
}
export interface FlagRecord { 'flag' : boolean }
export type FlagResult = { 'Ok' : FlagRecord } |
  { 'Err' : ApiError };
export interface GameStateCanister {
  'addChallenge' : ActorMethod<[NewChallengeInput], ChallengeAdditionResult>,
  'addChallengeTopic' : ActorMethod<
    [ChallengeTopicInput],
    ChallengeTopicResult
  >,
  'addLlmCanisterToMainer' : ActorMethod<
    [OfficialMainerAgentCanister],
    SetUpMainerLlmCanisterResult
  >,
  'addMainerAgentCanister' : ActorMethod<
    [OfficialMainerAgentCanister],
    MainerAgentCanisterResult
  >,
  'addMainerAgentCanisterAdmin' : ActorMethod<
    [OfficialMainerAgentCanister],
    MainerAgentCanisterResult
  >,
  'addOfficialCanister' : ActorMethod<[CanisterInput], StatusCodeRecordResult>,
  'addScoredResponse' : ActorMethod<
    [ScoredResponseInput],
    ScoredResponseResult
  >,
  'backupMainersAdmin' : ActorMethod<[], NatResult>,
  'cleanUnlockedMainerStoragesAdmin' : ActorMethod<[], AuthRecordResult>,
  'createUserMainerAgent' : ActorMethod<
    [MainerCreationInput],
    MainerAgentCanisterResult
  >,
  'deriveNewMainerAgentCanisterWasmHashAdmin' : ActorMethod<
    [DeriveWasmHashInput],
    CanisterWasmHashRecordResult
  >,
  'downloadJudgePromptCacheBytesChunk' : ActorMethod<
    [DownloadJudgePromptCacheBytesChunkInput],
    DownloadJudgePromptCacheBytesChunkRecordResult
  >,
  'downloadMainerPromptCacheBytesChunk' : ActorMethod<
    [DownloadMainerPromptCacheBytesChunkInput],
    DownloadMainerPromptCacheBytesChunkRecordResult
  >,
  'finishUploadJudgePromptCache' : ActorMethod<
    [FinishUploadJudgePromptCacheInput],
    StatusCodeRecordResult
  >,
  'finishUploadMainerPromptCache' : ActorMethod<
    [FinishUploadMainerPromptCacheInput],
    StatusCodeRecordResult
  >,
  'getArchivedChallengesAdmin' : ActorMethod<[], ChallengesResult>,
  'getBufferMainerCreation' : ActorMethod<[], NatResult>,
  'getCanisterPrincipal' : ActorMethod<[], string>,
  'getClosedChallengesAdmin' : ActorMethod<[], ChallengesResult>,
  'getCurrentChallenges' : ActorMethod<[], ChallengesResult>,
  'getCurrentChallengesAdmin' : ActorMethod<[], ChallengesResult>,
  'getCyclesBurnRate' : ActorMethod<
    [CyclesBurnRateDefault],
    CyclesBurnRateResult
  >,
  'getCyclesFlowAdmin' : ActorMethod<[], CyclesFlowResult>,
  'getGameStateThresholdsAdmin' : ActorMethod<[], GameStateTresholdsResult>,
  'getIsWhitelistPhaseActive' : ActorMethod<[], FlagResult>,
  'getJudgePromptInfo' : ActorMethod<[string], JudgePromptInfoResult>,
  'getLimitForCreatingMainerAdmin' : ActorMethod<[CheckMainerLimit], NatResult>,
  'getMainerAgentCanisterInfo' : ActorMethod<
    [CanisterRetrieveInput],
    MainerAgentCanisterResult
  >,
  'getMainerAgentCanistersAdmin' : ActorMethod<[], MainerAgentCanistersResult>,
  'getMainerAgentCanistersForUser' : ActorMethod<
    [],
    MainerAgentCanistersResult
  >,
  'getMainerCyclesUsedPerResponse' : ActorMethod<[], NatResult>,
  'getMainerPromptInfo' : ActorMethod<[string], MainerPromptInfoResult>,
  'getNextSubmissionToJudge' : ActorMethod<
    [],
    ChallengeResponseSubmissionResult
  >,
  'getNumArchivedChallengesAdmin' : ActorMethod<[], NatResult>,
  'getNumClosedChallengesAdmin' : ActorMethod<[], NatResult>,
  'getNumCurrentChallengesAdmin' : ActorMethod<[], NatResult>,
  'getNumOpenSubmissionsAdmin' : ActorMethod<[], NatResult>,
  'getNumOpenSubmissionsForOpenChallengesAdmin' : ActorMethod<[], NatResult>,
  'getNumScoredChallengesAdmin' : ActorMethod<[], NatResult>,
  'getNumSubmissionsAdmin' : ActorMethod<[], NatResult>,
  'getNumberMainerAgentsAdmin' : ActorMethod<[CheckMainerLimit], NatResult>,
  'getOfficialCanistersAdmin' : ActorMethod<
    [],
    Array<OfficialProtocolCanister>
  >,
  'getOfficialChallengerCanisters' : ActorMethod<[], AuthRecordResult>,
  'getOpenSubmissionsAdmin' : ActorMethod<
    [],
    ChallengeResponseSubmissionsResult
  >,
  'getOpenSubmissionsForOpenChallengesAdmin' : ActorMethod<
    [],
    ChallengeResponseSubmissionsResult
  >,
  'getPauseProtocolFlag' : ActorMethod<[], FlagResult>,
  'getPauseWhitelistMainerCreationFlag' : ActorMethod<[], FlagResult>,
  'getPriceForOwnMainer' : ActorMethod<[], PriceResult>,
  'getPriceForShareAgent' : ActorMethod<[], PriceResult>,
  'getProtocolCyclesBalanceBuffer' : ActorMethod<[], NatResult>,
  'getProtocolTotalCyclesBurnt' : ActorMethod<[], CyclesBurntResult>,
  'getRandomOpenChallenge' : ActorMethod<[], ChallengeResult>,
  'getRandomOpenChallengeTopic' : ActorMethod<[], ChallengeTopicResult>,
  'getRecentChallengeWinners' : ActorMethod<[], ChallengeWinnersResult>,
  'getRecentProtocolActivity' : ActorMethod<[], ProtocolActivityResult>,
  'getRedeemedTransactionBlockAdmin' : ActorMethod<
    [PaymentTransactionBlockId],
    RedeemedTransactionBlockResult
  >,
  'getRewardPerChallengeAdmin' : ActorMethod<[], RewardPerChallengeResult>,
  'getScoreForSubmission' : ActorMethod<
    [SubmissionRetrievalInput],
    ScoredResponseRetrievalResult
  >,
  'getScoredChallengesAdmin' : ActorMethod<[], ScoredChallengesResult>,
  'getSharedServiceCanistersAdmin' : ActorMethod<
    [],
    OfficialProtocolCanistersResult
  >,
  'getSubmissionsAdmin' : ActorMethod<[], ChallengeResponseSubmissionsResult>,
  'getSubnetsAdmin' : ActorMethod<[], SubnetIdsResult>,
  'getWhitelistPriceForOwnMainer' : ActorMethod<[], PriceResult>,
  'getWhitelistPriceForShareAgent' : ActorMethod<[], PriceResult>,
  'health' : ActorMethod<[], StatusCodeRecordResult>,
  'migrateArchivedChallengesAdmin' : ActorMethod<[], NatResult>,
  'reinstallMainerControllerAdmin' : ActorMethod<
    [MainerctrlReinstallInput],
    MainerAgentCanisterResult
  >,
  'removeRedeemedTransactionBlockAdmin' : ActorMethod<
    [PaymentTransactionBlockId],
    TextResult
  >,
  'removeSharedServiceCanisterAdmin' : ActorMethod<
    [{ 'canisterId' : string }],
    StatusCodeRecordResult
  >,
  'resetCurrentChallengesAdmin' : ActorMethod<[], StatusCodeRecordResult>,
  'resetCyclesFlowAdmin' : ActorMethod<[], StatusCodeRecordResult>,
  'setArchiveCanisterId' : ActorMethod<[string], AuthRecordResult>,
  'setBufferMainerCreation' : ActorMethod<[bigint], AuthRecordResult>,
  'setCyclesBurnRateAdmin' : ActorMethod<
    [SetCyclesBurnRateInput],
    StatusCodeRecordResult
  >,
  'setCyclesFlowAdmin' : ActorMethod<
    [CyclesFlowSettings],
    StatusCodeRecordResult
  >,
  'setGameStateThresholdsAdmin' : ActorMethod<
    [GameStateTresholds],
    StatusCodeRecordResult
  >,
  'setIcpForOwnMainerAdmin' : ActorMethod<[bigint], StatusCodeRecordResult>,
  'setIcpForShareAgentAdmin' : ActorMethod<[bigint], StatusCodeRecordResult>,
  'setIcpForWhitelistOwnMainerAdmin' : ActorMethod<
    [bigint],
    StatusCodeRecordResult
  >,
  'setIcpForWhitelistShareAgentAdmin' : ActorMethod<
    [bigint],
    StatusCodeRecordResult
  >,
  'setInitialChallengeTopics' : ActorMethod<[], StatusCodeRecordResult>,
  'setLimitForCreatingMainerAdmin' : ActorMethod<
    [MainerLimitInput],
    AuthRecordResult
  >,
  'setOfficialMainerAgentCanisterWasmHashAdmin' : ActorMethod<
    [UpdateWasmHashInput],
    CanisterWasmHashRecordResult
  >,
  'setProtocolCyclesBalanceBuffer' : ActorMethod<[bigint], AuthRecordResult>,
  'setRewardPerChallengeAdmin' : ActorMethod<
    [bigint],
    RewardPerChallengeResult
  >,
  'setSubnetsAdmin' : ActorMethod<[SubnetIds], StatusCodeRecordResult>,
  'setTokenLedgerCanisterId' : ActorMethod<[string], AuthRecordResult>,
  'setUpMainerLlmCanister' : ActorMethod<
    [OfficialMainerAgentCanister],
    SetUpMainerLlmCanisterResult
  >,
  'shouldCreatingMainersBeStopped' : ActorMethod<
    [CheckMainerLimit],
    FlagResult
  >,
  'spinUpMainerControllerCanister' : ActorMethod<
    [OfficialMainerAgentCanister],
    MainerAgentCanisterResult
  >,
  'spinUpMainerControllerCanisterForUserAdmin' : ActorMethod<
    [OfficialMainerAgentCanister],
    MainerAgentCanisterResult
  >,
  'startUploadJudgePromptCache' : ActorMethod<
    [],
    StartUploadJudgePromptCacheRecordResult
  >,
  'startUploadMainerPromptCache' : ActorMethod<
    [],
    StartUploadMainerPromptCacheRecordResult
  >,
  'submitChallengeResponse' : ActorMethod<
    [ChallengeResponseSubmissionInput],
    ChallengeResponseSubmissionMetadataResult
  >,
  'testMainerCodeIntegrityAdmin' : ActorMethod<[], AuthRecordResult>,
  'testTokenMintingAdmin' : ActorMethod<[], AuthRecordResult>,
  'togglePauseProtocolFlagAdmin' : ActorMethod<[], AuthRecordResult>,
  'togglePauseWhitelistMainerCreationFlagAdmin' : ActorMethod<
    [],
    AuthRecordResult
  >,
  'toggleWhitelistPhaseActiveFlagAdmin' : ActorMethod<[], AuthRecordResult>,
  'topUpCyclesForMainerAgent' : ActorMethod<
    [MainerAgentTopUpInput],
    MainerAgentCanisterResult
  >,
  'unlockUserMainerAgent' : ActorMethod<
    [MainerCreationInput],
    MainerAgentCanisterResult
  >,
  'upgradeMainerControllerAdmin' : ActorMethod<
    [MainerctrlUpgradeInput],
    MainerAgentCanisterResult
  >,
  'uploadJudgePromptCacheBytesChunk' : ActorMethod<
    [UploadJudgePromptCacheBytesChunkInput],
    StatusCodeRecordResult
  >,
  'uploadMainerPromptCacheBytesChunk' : ActorMethod<
    [UploadMainerPromptCacheBytesChunkInput],
    StatusCodeRecordResult
  >,
  'whitelistCreateUserMainerAgent' : ActorMethod<
    [WhitelistMainerCreationInput],
    MainerAgentCanisterResult
  >,
}
export interface GameStateTresholds {
  'thresholdMaxOpenSubmissions' : bigint,
  'thresholdMaxOpenChallenges' : bigint,
  'thresholdArchiveClosedChallenges' : bigint,
  'thresholdScoredResponsesPerChallenge' : bigint,
}
export type GameStateTresholdsResult = { 'Ok' : GameStateTresholds } |
  { 'Err' : ApiError };
export interface JudgePromptInfo {
  'promptCacheFilename' : string,
  'promptText' : string,
  'promptCacheNumberOfChunks' : bigint,
  'promptCacheSha256' : string,
}
export type JudgePromptInfoResult = { 'Ok' : JudgePromptInfo } |
  { 'Err' : ApiError };
export type List = [] | [[ScoredResponse, List]];
export type List_1 = [] | [[ChallengeParticipantEntry, List_1]];
export type LlmSetupStatus = { 'CodeInstallInProgress' : null } |
  { 'CanisterCreated' : null } |
  { 'ConfigurationInProgress' : null } |
  { 'CanisterCreationInProgress' : null } |
  { 'ModelUploadProgress' : number };
export type MainerAgentCanisterResult = { 'Ok' : OfficialMainerAgentCanister } |
  { 'Err' : ApiError };
export type MainerAgentCanisterType = { 'NA' : null } |
  { 'Own' : null } |
  { 'ShareAgent' : null } |
  { 'ShareService' : null };
export type MainerAgentCanistersResult = {
    'Ok' : Array<OfficialMainerAgentCanister>
  } |
  { 'Err' : ApiError };
export interface MainerAgentTopUpInput {
  'paymentTransactionBlockId' : bigint,
  'mainerAgent' : OfficialMainerAgentCanister,
}
export interface MainerConfigurationInput {
  'selectedLLM' : [] | [SelectableMainerLLMs],
  'subnetLlm' : string,
  'mainerAgentCanisterType' : MainerAgentCanisterType,
  'cyclesForMainer' : bigint,
  'subnetCtrl' : string,
}
export interface MainerCreationInput {
  'owner' : [] | [Principal],
  'paymentTransactionBlockId' : bigint,
  'mainerConfig' : MainerConfigurationInput,
}
export interface MainerLimitInput {
  'mainerType' : MainerAgentCanisterType,
  'newLimit' : bigint,
}
export interface MainerPromptInfo {
  'promptCacheFilename' : string,
  'promptText' : string,
  'promptCacheNumberOfChunks' : bigint,
  'promptCacheSha256' : string,
}
export type MainerPromptInfoResult = { 'Ok' : MainerPromptInfo } |
  { 'Err' : ApiError };
export interface MainerctrlReinstallInput {
  'canisterAddress' : CanisterAddress,
}
export interface MainerctrlUpgradeInput { 'canisterAddress' : CanisterAddress }
export type NatResult = { 'Ok' : bigint } |
  { 'Err' : ApiError };
export interface NewChallengeInput {
  'challengeTopicStatus' : ChallengeTopicStatus,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeTopicId' : string,
  'mainerPromptId' : string,
  'mainerMaxContinueLoopCount' : bigint,
  'mainerTemp' : number,
  'challengeQuestionSeed' : number,
  'mainerNumTokens' : bigint,
  'challengeQuestion' : string,
  'challengeTopic' : string,
  'cyclesGenerateChallengeChctrlChllm' : bigint,
  'judgePromptId' : string,
  'cyclesGenerateChallengeGsChctrl' : bigint,
}
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
export interface OfficialProtocolCanister {
  'status' : CanisterStatus,
  'canisterType' : ProtocolCanisterType,
  'ownedBy' : Principal,
  'creationTimestamp' : bigint,
  'createdBy' : Principal,
  'subnet' : string,
  'address' : CanisterAddress,
}
export type OfficialProtocolCanistersResult = {
    'Ok' : Array<OfficialProtocolCanister>
  } |
  { 'Err' : ApiError };
export interface PaymentTransactionBlockId {
  'paymentTransactionBlockId' : bigint,
}
export interface PriceRecord { 'price' : bigint }
export type PriceResult = { 'Ok' : PriceRecord } |
  { 'Err' : ApiError };
export interface ProtocolActivityRecord {
  'challenges' : Array<Challenge>,
  'winners' : Array<ChallengeWinnerDeclaration>,
}
export type ProtocolActivityResult = { 'Ok' : ProtocolActivityRecord } |
  { 'Err' : ApiError };
export type ProtocolCanisterType = { 'MainerAgent' : MainerAgentCanisterType } |
  { 'MainerLlm' : null } |
  { 'Challenger' : null } |
  { 'Judge' : null } |
  { 'Verifier' : null } |
  { 'MainerCreator' : null };
export type RedeemedForOptions = {
    'MainerCreation' : MainerAgentCanisterType
  } |
  { 'MainerTopUp' : CanisterAddress };
export interface RedeemedTransactionBlock {
  'redeemedBy' : Principal,
  'creationTimestamp' : bigint,
  'paymentTransactionBlockId' : bigint,
  'redeemedFor' : RedeemedForOptions,
  'amount' : bigint,
}
export type RedeemedTransactionBlockResult = {
    'Ok' : RedeemedTransactionBlock
  } |
  { 'Err' : ApiError };
export interface RewardPerChallenge {
  'amountForAllParticipants' : bigint,
  'thirdPlaceAmount' : bigint,
  'rewardType' : RewardType,
  'totalAmount' : bigint,
  'winnerAmount' : bigint,
  'secondPlaceAmount' : bigint,
}
export type RewardPerChallengeResult = { 'Ok' : RewardPerChallenge } |
  { 'Err' : ApiError };
export type RewardType = { 'ICP' : null } |
  { 'Coupon' : string } |
  { 'MainerToken' : null } |
  { 'Cycles' : null } |
  { 'Other' : string };
export type ScoredChallengesResult = { 'Ok' : Array<[string, List]> } |
  { 'Err' : ApiError };
export interface ScoredResponse {
  'challengeClosedTimestamp' : [] | [bigint],
  'challengeTopicStatus' : ChallengeTopicStatus,
  'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : bigint,
  'protocolOperationFeesCut' : bigint,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeCreationTimestamp' : bigint,
  'challengeCreatedBy' : CanisterAddress,
  'challengeTopicId' : string,
  'cyclesGenerateResponseOwnctrlOwnllmHIGH' : bigint,
  'judgedBy' : Principal,
  'submittedTimestamp' : bigint,
  'cyclesGenerateResponseOwnctrlOwnllmLOW' : bigint,
  'mainerPromptId' : string,
  'cyclesGenerateResponseSsctrlSsllm' : bigint,
  'mainerMaxContinueLoopCount' : bigint,
  'submittedBy' : Principal,
  'mainerTemp' : number,
  'challengeStatus' : ChallengeStatus,
  'cyclesGenerateResponseOwnctrlGs' : bigint,
  'challengeQuestionSeed' : number,
  'mainerNumTokens' : bigint,
  'submissionStatus' : ChallengeResponseSubmissionStatus,
  'score' : bigint,
  'challengeQuestion' : string,
  'challengeId' : string,
  'challengeQueuedBy' : Principal,
  'challengeQueuedId' : string,
  'challengeQueuedTo' : Principal,
  'challengeTopic' : string,
  'judgedTimestamp' : bigint,
  'cyclesGenerateChallengeChctrlChllm' : bigint,
  'cyclesGenerateScoreGsJuctrl' : bigint,
  'cyclesGenerateResponseSactrlSsctrl' : bigint,
  'judgePromptId' : string,
  'submissionId' : string,
  'challengeAnswerSeed' : number,
  'challengeAnswer' : string,
  'challengeQueuedTimestamp' : bigint,
  'cyclesSubmitResponse' : bigint,
  'scoreSeed' : number,
  'cyclesGenerateChallengeGsChctrl' : bigint,
  'cyclesGenerateScoreJuctrlJullm' : bigint,
  'cyclesGenerateResponseSsctrlGs' : bigint,
}
export interface ScoredResponseInput {
  'challengeClosedTimestamp' : [] | [bigint],
  'challengeTopicStatus' : ChallengeTopicStatus,
  'cyclesGenerateResponseOwnctrlOwnllmMEDIUM' : bigint,
  'protocolOperationFeesCut' : bigint,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeCreationTimestamp' : bigint,
  'challengeCreatedBy' : CanisterAddress,
  'challengeTopicId' : string,
  'cyclesGenerateResponseOwnctrlOwnllmHIGH' : bigint,
  'judgedBy' : Principal,
  'submittedTimestamp' : bigint,
  'cyclesGenerateResponseOwnctrlOwnllmLOW' : bigint,
  'mainerPromptId' : string,
  'cyclesGenerateResponseSsctrlSsllm' : bigint,
  'mainerMaxContinueLoopCount' : bigint,
  'submittedBy' : Principal,
  'mainerTemp' : number,
  'challengeStatus' : ChallengeStatus,
  'cyclesGenerateResponseOwnctrlGs' : bigint,
  'challengeQuestionSeed' : number,
  'mainerNumTokens' : bigint,
  'submissionStatus' : ChallengeResponseSubmissionStatus,
  'score' : bigint,
  'challengeQuestion' : string,
  'challengeId' : string,
  'challengeQueuedBy' : Principal,
  'challengeQueuedId' : string,
  'challengeQueuedTo' : Principal,
  'challengeTopic' : string,
  'cyclesGenerateChallengeChctrlChllm' : bigint,
  'cyclesGenerateScoreGsJuctrl' : bigint,
  'cyclesGenerateResponseSactrlSsctrl' : bigint,
  'judgePromptId' : string,
  'submissionId' : string,
  'challengeAnswerSeed' : number,
  'challengeAnswer' : string,
  'challengeQueuedTimestamp' : bigint,
  'cyclesSubmitResponse' : bigint,
  'scoreSeed' : number,
  'cyclesGenerateChallengeGsChctrl' : bigint,
  'cyclesGenerateScoreJuctrlJullm' : bigint,
  'cyclesGenerateResponseSsctrlGs' : bigint,
}
export type ScoredResponseResult = { 'Ok' : ScoredResponseReturn } |
  { 'Err' : ApiError };
export type ScoredResponseRetrievalResult = { 'Ok' : ScoredResponse } |
  { 'Err' : ApiError };
export interface ScoredResponseReturn { 'success' : boolean }
export type SelectableMainerLLMs = { 'Qwen2_5_500M' : null };
export interface SetCyclesBurnRateInput {
  'cyclesBurnRate' : CyclesBurnRate,
  'cyclesBurnRateDefault' : CyclesBurnRateDefault,
}
export type SetUpMainerLlmCanisterResult = {
    'Ok' : {
      'llmCanisterId' : string,
      'controllerCanisterEntry' : OfficialMainerAgentCanister,
    }
  } |
  { 'Err' : ApiError };
export interface StartUploadJudgePromptCacheRecord { 'judgePromptId' : string }
export type StartUploadJudgePromptCacheRecordResult = {
    'Ok' : StartUploadJudgePromptCacheRecord
  } |
  { 'Err' : ApiError };
export interface StartUploadMainerPromptCacheRecord {
  'mainerPromptId' : string,
}
export type StartUploadMainerPromptCacheRecordResult = {
    'Ok' : StartUploadMainerPromptCacheRecord
  } |
  { 'Err' : ApiError };
export type StatusCode = number;
export interface StatusCodeRecord { 'status_code' : StatusCode }
export type StatusCodeRecordResult = { 'Ok' : StatusCodeRecord } |
  { 'Err' : ApiError };
export interface SubmissionRetrievalInput {
  'challengeId' : string,
  'submissionId' : string,
}
export interface SubnetIds {
  'subnetShareServiceCtrl' : string,
  'subnetShareAgentCtrl' : string,
  'subnetShareServiceLlm' : string,
}
export type SubnetIdsResult = { 'Ok' : SubnetIds } |
  { 'Err' : ApiError };
export type TextResult = { 'Ok' : string } |
  { 'Err' : ApiError };
export type TimeInterval = { 'Daily' : null };
export interface UpdateWasmHashInput {
  'wasmHash' : Uint8Array | number[],
  'textNote' : string,
}
export interface UploadJudgePromptCacheBytesChunkInput {
  'chunkID' : bigint,
  'bytesChunk' : Uint8Array | number[],
  'judgePromptId' : string,
}
export interface UploadMainerPromptCacheBytesChunkInput {
  'mainerPromptId' : string,
  'chunkID' : bigint,
  'bytesChunk' : Uint8Array | number[],
}
export interface WhitelistMainerCreationInput {
  'status' : CanisterStatus,
  'canisterType' : ProtocolCanisterType,
  'ownedBy' : Principal,
  'owner' : [] | [Principal],
  'creationTimestamp' : bigint,
  'createdBy' : Principal,
  'paymentTransactionBlockId' : bigint,
  'mainerConfig' : MainerConfigurationInput,
  'subnet' : string,
  'address' : CanisterAddress,
}
export interface _SERVICE extends GameStateCanister {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
