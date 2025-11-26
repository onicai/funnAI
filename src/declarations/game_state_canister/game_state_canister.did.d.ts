import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export interface Account {
  'owner' : Principal,
  'subaccount' : [] | [Uint8Array | number[]],
}
export interface Account__1 {
  'owner' : Principal,
  'subaccount' : [] | [Subaccount],
}
export interface AddCyclesRecord { 'added' : boolean, 'amount' : bigint }
export type AddCyclesResult = { 'Ok' : AddCyclesRecord } |
  { 'Err' : ApiError };
export type ApiError = { 'FailedOperation' : null } |
  { 'InvalidId' : null } |
  { 'ZeroAddress' : null } |
  { 'Unauthorized' : null } |
  { 'StatusCode' : StatusCode } |
  { 'Other' : string } |
  { 'InsuffientCycles' : bigint };
export interface ApprovalInfo {
  'memo' : [] | [Uint8Array | number[]],
  'from_subaccount' : [] | [Uint8Array | number[]],
  'created_at_time' : [] | [bigint],
  'expires_at' : [] | [bigint],
  'spender' : Account__1,
}
export interface ApproveTokenArg {
  'token_id' : bigint,
  'approval_info' : ApprovalInfo,
}
export type ApproveTokenError = {
    'GenericError' : { 'message' : string, 'error_code' : bigint }
  } |
  { 'Duplicate' : { 'duplicate_of' : bigint } } |
  { 'InvalidSpender' : null } |
  { 'NonExistingTokenId' : null } |
  { 'Unauthorized' : null } |
  { 'CreatedInFuture' : { 'ledger_time' : bigint } } |
  { 'GenericBatchError' : { 'message' : string, 'error_code' : bigint } } |
  { 'TooOld' : null };
export type ApproveTokenResult = { 'Ok' : bigint } |
  { 'Err' : ApproveTokenError };
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
export type ChallengeResponseSubmissionStatus = { 'Judged' : null } |
  { 'FailedSubmission' : null } |
  { 'Processed' : null } |
  { 'Judging' : null } |
  { 'Received' : null } |
  { 'Other' : string } |
  { 'Submitted' : null };
export interface ChallengeResponseSubmissionWithQueueStatus {
  'remainingInQueue' : bigint,
  'submission' : ChallengeResponseSubmission,
}
export type ChallengeResponseSubmissionWithQueueStatusResult = {
    'Ok' : ChallengeResponseSubmissionWithQueueStatus
  } |
  { 'Err' : ApiError };
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
export interface CyclesTransaction {
  'newOfficialCycleBalance' : bigint,
  'creationTimestamp' : bigint,
  'amountAdded' : bigint,
  'sentBy' : Principal,
  'previousCyclesBalance' : bigint,
  'succeeded' : boolean,
}
export type CyclesTransactionsResult = { 'Ok' : Array<CyclesTransaction> } |
  { 'Err' : ApiError };
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
  'addCycles' : ActorMethod<[], AddCyclesResult>,
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
  'archiveSubmissionsAdmin' : ActorMethod<[], NatResult>,
  'backupMainersAdmin' : ActorMethod<[], NatResult>,
  'cancelMarketplaceReservation' : ActorMethod<
    [MainerMarketplaceReservationInput],
    StatusCodeRecordResult
  >,
  'checkUserMainerMappingConsistencyAdmin' : ActorMethod<[], AuthRecordResult>,
  'cleanOpenSubmissionsQueueAdmin' : ActorMethod<[], NatResult>,
  'cleanSubmissionsAdmin' : ActorMethod<[], AuthRecordResult>,
  'cleanUnlockedMainerStoragesAdmin' : ActorMethod<[], AuthRecordResult>,
  'clearMarketplaceReservationsAdmin' : ActorMethod<[], AuthRecordResult>,
  'completeMainerSetupForUserAdmin' : ActorMethod<
    [OfficialMainerAgentCanister],
    MainerAgentCanisterResult
  >,
  'confirmUserMarketplaceMainerReservation' : ActorMethod<
    [MainerMarketplaceReservationInput],
    MainerMarketplaceReservationResult
  >,
  'createUserMainerAgent' : ActorMethod<
    [MainerCreationInput],
    MainerAgentCanisterResult
  >,
  'deriveNewMainerAgentCanisterWasmHashAdmin' : ActorMethod<
    [DeriveWasmHashInput],
    CanisterWasmHashRecordResult
  >,
  'disburseIcpToTreasuryAdmin' : ActorMethod<[], AuthRecordResult>,
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
  'getAvailableMainers' : ActorMethod<[], NatResult>,
  'getBufferMainerCreation' : ActorMethod<[], NatResult>,
  'getCanisterPrincipal' : ActorMethod<[], string>,
  'getClosedChallengesAdmin' : ActorMethod<[], ChallengesResult>,
  'getCurrentChallenges' : ActorMethod<[], ChallengesResult>,
  'getCurrentChallengesAdmin' : ActorMethod<[], ChallengesResult>,
  'getCyclesBalanceThresholdFunnaiTopups' : ActorMethod<[], NatResult>,
  'getCyclesBurnRate' : ActorMethod<
    [CyclesBurnRateDefault],
    CyclesBurnRateResult
  >,
  'getCyclesFlowAdmin' : ActorMethod<[], CyclesFlowResult>,
  'getCyclesTransactionsAdmin' : ActorMethod<[], CyclesTransactionsResult>,
  'getDisburseFundsToTreasuryFlag' : ActorMethod<[], FlagResult>,
  'getFunnaiCyclesPrice' : ActorMethod<[], NatResult>,
  'getFunnaiCyclesPriceAdmin' : ActorMethod<[], NatResult>,
  'getGameStateThresholdsAdmin' : ActorMethod<[], GameStateTresholdsResult>,
  'getIsMainerAuctionActive' : ActorMethod<[], FlagResult>,
  'getIsMigratingChallengesFlagAdmin' : ActorMethod<[], FlagResult>,
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
  'getMainerAgentCanistersForUserAdmin' : ActorMethod<
    [string],
    MainerAgentCanistersResult
  >,
  'getMainerAuctionTimerInfo' : ActorMethod<[], MainerAuctionTimerInfoResult>,
  'getMainerCyclesUsedPerResponse' : ActorMethod<[], NatResult>,
  'getMainerPromptInfo' : ActorMethod<[string], MainerPromptInfoResult>,
  'getMarketplaceMainerListings' : ActorMethod<
    [],
    MainerMarketplaceListingsResult
  >,
  'getMarketplaceSalesStats' : ActorMethod<[], MarketplaceStats>,
  'getMaxFunnaiTopupCyclesAmount' : ActorMethod<[], NatResult>,
  'getMaxFunnaiTopupCyclesAmountAdmin' : ActorMethod<[], NatResult>,
  'getMinimumIcpBalance' : ActorMethod<[], NatResult>,
  'getNextMainerAuctionPriceDropAtNs' : ActorMethod<[], NatResult>,
  'getNextSubmissionToJudge' : ActorMethod<
    [],
    ChallengeResponseSubmissionWithQueueStatusResult
  >,
  'getNumArchivedChallengesAdmin' : ActorMethod<[], NatResult>,
  'getNumArchivedSubmissionsAdmin' : ActorMethod<[], NatResult>,
  'getNumClosedChallengesAdmin' : ActorMethod<[], NatResult>,
  'getNumCurrentChallengesAdmin' : ActorMethod<[], NatResult>,
  'getNumMainerAgentCanistersForUserAdmin' : ActorMethod<[string], NatResult>,
  'getNumOpenSubmissionsAdmin' : ActorMethod<[], NatResult>,
  'getNumOpenSubmissionsForOpenChallengesAdmin' : ActorMethod<[], NatResult>,
  'getNumScoredChallengesAdmin' : ActorMethod<[], NatResult>,
  'getNumSubmissionsAdmin' : ActorMethod<[], NatResult>,
  'getNumSubmissionsToMigrateAdmin' : ActorMethod<[], NatResult>,
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
  'getOpenSubmissionsQueueSizeAdmin' : ActorMethod<[], NatResult>,
  'getPauseProtocolFlag' : ActorMethod<[], FlagResult>,
  'getPauseWhitelistMainerCreationFlag' : ActorMethod<[], FlagResult>,
  'getPriceForOwnMainer' : ActorMethod<[], PriceResult>,
  'getPriceForShareAgent' : ActorMethod<[], PriceResult>,
  'getProtocolCyclesBalanceBuffer' : ActorMethod<[], NatResult>,
  'getProtocolTotalCyclesBurnt' : ActorMethod<[], CyclesBurntResult>,
  'getRandomOpenChallenge' : ActorMethod<[], ChallengeResult>,
  'getRandomOpenChallengeAdmin' : ActorMethod<[], ChallengeResult>,
  'getRandomOpenChallengeTopic' : ActorMethod<[], ChallengeTopicResult>,
  'getRandomOpenChallengeTopicAdmin' : ActorMethod<[], ChallengeTopicResult>,
  'getRecentChallengeWinners' : ActorMethod<[], ChallengeWinnersResult>,
  'getRecentProtocolActivity' : ActorMethod<[], ProtocolActivityResult>,
  'getRedeemedFunnaiTransactionBlockAdmin' : ActorMethod<
    [PaymentTransactionBlockId],
    RedeemedTransactionBlockResult
  >,
  'getRedeemedFunnaiTransactionBlocksAdmin' : ActorMethod<
    [],
    RedeemedTransactionBlocksResult
  >,
  'getRedeemedTransactionBlockAdmin' : ActorMethod<
    [PaymentTransactionBlockId],
    RedeemedTransactionBlockResult
  >,
  'getRedeemedTransactionBlocksAdmin' : ActorMethod<
    [],
    RedeemedTransactionBlocksResult
  >,
  'getRewardPerChallengeAdmin' : ActorMethod<[], RewardPerChallengeResult>,
  'getRoundRobinChallengeIndexAdmin' : ActorMethod<[], NatResult>,
  'getRoundRobinTopicIndexAdmin' : ActorMethod<[], NatResult>,
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
  'getTreasuryCanisterId' : ActorMethod<[], string>,
  'getUserMarketplaceMainerListings' : ActorMethod<
    [],
    MainerMarketplaceListingsResult
  >,
  'getUserMarketplaceReservation' : ActorMethod<
    [],
    [] | [MainerMarketplaceListing]
  >,
  'getUserMarketplaceTransactionHistory' : ActorMethod<
    [],
    MarketplaceTransactionHistoryResult
  >,
  'getWhitelistPriceForOwnMainer' : ActorMethod<[], PriceResult>,
  'getWhitelistPriceForShareAgent' : ActorMethod<[], PriceResult>,
  'health' : ActorMethod<[], StatusCodeRecordResult>,
  'icrc10_supported_standards' : ActorMethod<[], SupportedStandards>,
  'icrc37_approve_tokens' : ActorMethod<
    [Array<ApproveTokenArg>],
    Array<[] | [ApproveTokenResult]>
  >,
  'icrc37_revoke_token_approvals' : ActorMethod<
    [Array<RevokeTokenApprovalArg>],
    Array<[] | [RevokeTokenApprovalResult]>
  >,
  'icrc37_transfer_from' : ActorMethod<
    [Array<TransferFromArg>],
    Array<[] | [TransferFromResult]>
  >,
  'icrc7_balance_of' : ActorMethod<[Array<Account>], Array<bigint>>,
  'icrc7_collection_metadata' : ActorMethod<[], Array<[string, Value]>>,
  'icrc7_description' : ActorMethod<[], [] | [string]>,
  'icrc7_logo' : ActorMethod<[], [] | [string]>,
  'icrc7_name' : ActorMethod<[], string>,
  'icrc7_supply_cap' : ActorMethod<[], [] | [bigint]>,
  'icrc7_symbol' : ActorMethod<[], string>,
  'icrc7_token_metadata' : ActorMethod<
    [Array<bigint>],
    Array<[] | [Array<[string, Value]>]>
  >,
  'icrc7_tokens' : ActorMethod<[[] | [bigint], [] | [bigint]], Array<bigint>>,
  'icrc7_total_supply' : ActorMethod<[], bigint>,
  'initializeOpenSubmissionsQueueAdmin' : ActorMethod<[], AuthRecordResult>,
  'isMainerReservedOnMarketplaceAdmin' : ActorMethod<[string], boolean>,
  'migrateArchivedChallengesAdmin' : ActorMethod<[], NatResult>,
  'migrateScoredResponsesForChallengeAdmin' : ActorMethod<
    [string],
    AuthRecordResult
  >,
  'migrateSubmissionsAdmin' : ActorMethod<[], AuthRecordResult>,
  'migrateWinnerDeclarationsAdmin' : ActorMethod<
    [Array<string>],
    AuthRecordResult
  >,
  'reinstallMainerControllerAdmin' : ActorMethod<
    [MainerctrlReinstallInput],
    MainerAgentCanisterResult
  >,
  'removeRedeemedFunnaiTransactionBlockAdmin' : ActorMethod<
    [PaymentTransactionBlockId],
    TextResult
  >,
  'removeRedeemedTransactionBlockAdmin' : ActorMethod<
    [PaymentTransactionBlockId],
    TextResult
  >,
  'removeSharedServiceCanisterAdmin' : ActorMethod<
    [{ 'canisterId' : string }],
    StatusCodeRecordResult
  >,
  'reserveMarketplaceListedMainer' : ActorMethod<
    [MainerMarketplaceReservationInput],
    MainerMarketplaceReservationResult
  >,
  'resetCurrentChallengesAdmin' : ActorMethod<[], StatusCodeRecordResult>,
  'resetCyclesFlowAdmin' : ActorMethod<[], StatusCodeRecordResult>,
  'resetIsMigratingChallengesFlagAdmin' : ActorMethod<[], AuthRecordResult>,
  'resetRoundRobinChallengeIndexAdmin' : ActorMethod<
    [],
    StatusCodeRecordResult
  >,
  'resetRoundRobinTopicIndexAdmin' : ActorMethod<[], StatusCodeRecordResult>,
  'setApiCanisterId' : ActorMethod<[string], AuthRecordResult>,
  'setArchiveCanisterId' : ActorMethod<[string], AuthRecordResult>,
  'setAuctionIntervalSecondsAdmin' : ActorMethod<[bigint], AuthRecordResult>,
  'setAuctionPricesAdmin' : ActorMethod<
    [BigUint64Array | bigint[]],
    AuthRecordResult
  >,
  'setBufferMainerCreation' : ActorMethod<[bigint], AuthRecordResult>,
  'setCyclesBalanceThresholdFunnaiTopups' : ActorMethod<
    [bigint],
    AuthRecordResult
  >,
  'setCyclesBurnRateAdmin' : ActorMethod<
    [SetCyclesBurnRateInput],
    StatusCodeRecordResult
  >,
  'setCyclesFlowAdmin' : ActorMethod<
    [CyclesFlowSettings],
    StatusCodeRecordResult
  >,
  'setFunnaiCyclesPrice' : ActorMethod<[bigint], AuthRecordResult>,
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
  'setMaxFunnaiTopupCyclesAmount' : ActorMethod<[bigint], AuthRecordResult>,
  'setMinimumIcpBalance' : ActorMethod<[bigint], AuthRecordResult>,
  'setNumSubmissionsToMigrateAdmin' : ActorMethod<[bigint], NatResult>,
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
  'setTreasuryCanisterId' : ActorMethod<[string], AuthRecordResult>,
  'setUpMainerLlmCanister' : ActorMethod<
    [OfficialMainerAgentCanister],
    SetUpMainerLlmCanisterResult
  >,
  'setupAuctionAdmin' : ActorMethod<
    [BigUint64Array | bigint[], bigint],
    AuthRecordResult
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
  'startAuctionAdmin' : ActorMethod<[], AuthRecordResult>,
  'startUploadJudgePromptCache' : ActorMethod<
    [],
    StartUploadJudgePromptCacheRecordResult
  >,
  'startUploadMainerPromptCache' : ActorMethod<
    [],
    StartUploadMainerPromptCacheRecordResult
  >,
  'stopAuctionAdmin' : ActorMethod<[], AuthRecordResult>,
  'submitChallengeResponse' : ActorMethod<
    [ChallengeResponseSubmissionInput],
    ChallengeResponseSubmissionMetadataResult
  >,
  'testDisbursementToTreasuryAdmin' : ActorMethod<[], AuthRecordResult>,
  'testMainerCodeIntegrityAdmin' : ActorMethod<[], AuthRecordResult>,
  'testTokenMintingAdmin' : ActorMethod<[], AuthRecordResult>,
  'toggleDisburseFundsToTreasuryFlagAdmin' : ActorMethod<[], AuthRecordResult>,
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
  'topUpCyclesForMainerAgentWithFunnai' : ActorMethod<
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
export interface MainerAuctionTimerInfoRecord {
  'active' : boolean,
  'intervalSeconds' : bigint,
  'lastUpdateNs' : bigint,
}
export type MainerAuctionTimerInfoResult = {
    'Ok' : MainerAuctionTimerInfoRecord
  } |
  { 'Err' : ApiError };
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
export interface MainerMarketplaceListing {
  'listedTimestamp' : bigint,
  'listedBy' : Principal,
  'mainerType' : MainerAgentCanisterType,
  'address' : CanisterAddress,
  'reservedBy' : [] | [Principal],
  'priceE8S' : bigint,
}
export type MainerMarketplaceListingsResult = {
    'Ok' : Array<MainerMarketplaceListing>
  } |
  { 'Err' : ApiError };
export interface MainerMarketplaceReservationInput {
  'address' : CanisterAddress,
}
export type MainerMarketplaceReservationResult = {
    'Ok' : MainerMarketplaceListing
  } |
  { 'Err' : ApiError };
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
export interface MarketplaceSale {
  'mainerAddress' : string,
  'seller' : Principal,
  'buyer' : Principal,
  'saleTimestamp' : bigint,
  'priceE8S' : bigint,
}
export interface MarketplaceStats {
  'uniqueBuyers' : bigint,
  'uniqueSellers' : bigint,
  'totalVolumeE8S' : bigint,
  'totalSales' : bigint,
}
export interface MarketplaceTransactionHistory {
  'sales' : Array<MarketplaceSale>,
  'purchases' : Array<MarketplaceSale>,
}
export type MarketplaceTransactionHistoryResult = {
    'Ok' : MarketplaceTransactionHistory
  } |
  { 'Err' : ApiError };
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
export type RedeemedTransactionBlocksResult = {
    'Ok' : Array<RedeemedTransactionBlock>
  } |
  { 'Err' : ApiError };
export interface RevokeTokenApprovalArg {
  'token_id' : bigint,
  'memo' : [] | [Uint8Array | number[]],
  'from_subaccount' : [] | [Uint8Array | number[]],
  'created_at_time' : [] | [bigint],
  'spender' : [] | [Account__1],
}
export type RevokeTokenApprovalError = {
    'GenericError' : { 'message' : string, 'error_code' : bigint }
  } |
  { 'Duplicate' : { 'duplicate_of' : bigint } } |
  { 'NonExistingTokenId' : null } |
  { 'Unauthorized' : null } |
  { 'CreatedInFuture' : { 'ledger_time' : bigint } } |
  { 'ApprovalDoesNotExist' : null } |
  { 'GenericBatchError' : { 'message' : string, 'error_code' : bigint } } |
  { 'TooOld' : null };
export type RevokeTokenApprovalResult = { 'Ok' : bigint } |
  { 'Err' : RevokeTokenApprovalError };
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
export type Subaccount = Uint8Array | number[];
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
export type SupportedStandards = Array<{ 'url' : string, 'name' : string }>;
export type TextResult = { 'Ok' : string } |
  { 'Err' : ApiError };
export type TimeInterval = { 'Daily' : null };
export interface TransferFromArg {
  'to' : Account__1,
  'spender_subaccount' : [] | [Uint8Array | number[]],
  'token_id' : bigint,
  'from' : Account__1,
  'memo' : [] | [Uint8Array | number[]],
  'created_at_time' : [] | [bigint],
}
export type TransferFromError = {
    'GenericError' : { 'message' : string, 'error_code' : bigint }
  } |
  { 'Duplicate' : { 'duplicate_of' : bigint } } |
  { 'NonExistingTokenId' : null } |
  { 'Unauthorized' : null } |
  { 'CreatedInFuture' : { 'ledger_time' : bigint } } |
  { 'InvalidRecipient' : null } |
  { 'GenericBatchError' : { 'message' : string, 'error_code' : bigint } } |
  { 'TooOld' : null };
export type TransferFromResult = { 'Ok' : bigint } |
  { 'Err' : TransferFromError };
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
export type Value = { 'Int' : bigint } |
  { 'Map' : Array<[string, Value__1]> } |
  { 'Nat' : bigint } |
  { 'Blob' : Uint8Array | number[] } |
  { 'Text' : string } |
  { 'Array' : Array<Value__1> };
export type Value__1 = { 'Int' : bigint } |
  { 'Map' : Array<[string, Value__1]> } |
  { 'Nat' : bigint } |
  { 'Blob' : Uint8Array | number[] } |
  { 'Text' : string } |
  { 'Array' : Array<Value__1> };
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
