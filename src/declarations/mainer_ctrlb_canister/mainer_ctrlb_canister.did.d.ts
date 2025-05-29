import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

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
export interface AuthRecord { 'auth' : string }
export type AuthRecordResult = { 'Ok' : AuthRecord } |
  { 'Err' : ApiError };
export type CanisterAddress = string;
export type CanisterAddressesResult = { 'Ok' : Array<CanisterAddress> } |
  { 'Err' : ApiError };
export interface CanisterIDRecord { 'canister_id' : string }
export type CanisterIDRecordResult = { 'Ok' : CanisterIDRecord } |
  { 'Err' : ApiError };
export type CanisterStatus = { 'Paused' : null } |
  { 'Paid' : null } |
  { 'Unlocked' : null } |
  { 'LlmSetupFinished' : null } |
  { 'ControllerCreated' : null } |
  { 'LlmSetupInProgress' : LlmSetupStatus } |
  { 'Running' : null } |
  { 'Other' : string } |
  { 'ControllerCreationInProgress' : null };
export interface ChallengeQueueInput {
  'challengeClosedTimestamp' : [] | [bigint],
  'challengeTopicStatus' : ChallengeTopicStatus,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeCreationTimestamp' : bigint,
  'challengeCreatedBy' : CanisterAddress,
  'challengeTopicId' : string,
  'challengeStatus' : ChallengeStatus,
  'challengeQuestionSeed' : number,
  'challengeQuestion' : string,
  'challengeId' : string,
  'challengeQueuedBy' : Principal,
  'challengeQueuedId' : string,
  'challengeQueuedTo' : Principal,
  'challengeTopic' : string,
  'submissionCyclesRequired' : bigint,
  'challengeQueuedTimestamp' : bigint,
}
export type ChallengeQueueInputResult = { 'Ok' : ChallengeQueueInput } |
  { 'Err' : ApiError };
export type ChallengeQueueInputsResult = { 'Ok' : Array<ChallengeQueueInput> } |
  { 'Err' : ApiError };
export interface ChallengeResponseSubmission {
  'challengeClosedTimestamp' : [] | [bigint],
  'challengeTopicStatus' : ChallengeTopicStatus,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeCreationTimestamp' : bigint,
  'challengeCreatedBy' : CanisterAddress,
  'challengeTopicId' : string,
  'submittedTimestamp' : bigint,
  'submittedBy' : Principal,
  'challengeStatus' : ChallengeStatus,
  'challengeQuestionSeed' : number,
  'submissionStatus' : ChallengeResponseSubmissionStatus,
  'challengeQuestion' : string,
  'challengeId' : string,
  'challengeQueuedBy' : Principal,
  'challengeQueuedId' : string,
  'challengeQueuedTo' : Principal,
  'challengeTopic' : string,
  'submissionId' : string,
  'challengeAnswerSeed' : number,
  'submissionCyclesRequired' : bigint,
  'challengeAnswer' : string,
  'challengeQueuedTimestamp' : bigint,
}
export interface ChallengeResponseSubmissionInput {
  'challengeClosedTimestamp' : [] | [bigint],
  'challengeTopicStatus' : ChallengeTopicStatus,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeCreationTimestamp' : bigint,
  'challengeCreatedBy' : CanisterAddress,
  'challengeTopicId' : string,
  'submittedBy' : Principal,
  'challengeStatus' : ChallengeStatus,
  'challengeQuestionSeed' : number,
  'challengeQuestion' : string,
  'challengeId' : string,
  'challengeQueuedBy' : Principal,
  'challengeQueuedId' : string,
  'challengeQueuedTo' : Principal,
  'challengeTopic' : string,
  'challengeAnswerSeed' : number,
  'submissionCyclesRequired' : bigint,
  'challengeAnswer' : string,
  'challengeQueuedTimestamp' : bigint,
}
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
export type ChallengeStatus = { 'Open' : null } |
  { 'Closed' : null } |
  { 'Archived' : null } |
  { 'Other' : string };
export type ChallengeTopicStatus = { 'Open' : null } |
  { 'Closed' : null } |
  { 'Archived' : null } |
  { 'Other' : string };
export interface CyclesBurnRate {
  'cycles' : bigint,
  'timeInterval' : TimeInterval,
}
export type CyclesBurnRateDefault = { 'Low' : null } |
  { 'Mid' : null } |
  { 'VeryHigh' : null } |
  { 'High' : null } |
  { 'Custom' : CyclesBurnRate };
export interface IssueFlagsRecord { 'lowCycleBalance' : boolean }
export type IssueFlagsRetrievalResult = { 'Ok' : IssueFlagsRecord } |
  { 'Err' : ApiError };
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
export type MainerAgentCanisterTypeResult = { 'Ok' : MainerAgentCanisterType } |
  { 'Err' : ApiError };
export interface MainerAgentCtrlbCanister {
  'addChallengeResponseToShareAgent' : ActorMethod<
    [ChallengeResponseSubmissionInput],
    StatusCodeRecordResult
  >,
  'addChallengeToShareServiceQueue' : ActorMethod<
    [ChallengeQueueInput],
    ChallengeQueueInputResult
  >,
  'addCycles' : ActorMethod<[], AddCyclesResult>,
  'addMainerShareAgentCanister' : ActorMethod<
    [OfficialMainerAgentCanister],
    MainerAgentCanisterResult
  >,
  'addMainerShareAgentCanisterAdmin' : ActorMethod<
    [OfficialMainerAgentCanister],
    MainerAgentCanisterResult
  >,
  'add_llm_canister' : ActorMethod<[CanisterIDRecord], StatusCodeRecordResult>,
  'amiController' : ActorMethod<[], StatusCodeRecordResult>,
  'checkAccessToLLMs' : ActorMethod<[], StatusCodeRecordResult>,
  'getChallengeQueueAdmin' : ActorMethod<[], ChallengeQueueInputsResult>,
  'getGameStateCanisterId' : ActorMethod<[], string>,
  'getIssueFlagsAdmin' : ActorMethod<[], IssueFlagsRetrievalResult>,
  'getLLMCanisterIds' : ActorMethod<[], CanisterAddressesResult>,
  'getMainerCanisterType' : ActorMethod<[], MainerAgentCanisterTypeResult>,
  'getMainerStatisticsAdmin' : ActorMethod<[], StatisticsRetrievalResult>,
  'getRecentSubmittedResponsesAdmin' : ActorMethod<
    [],
    ChallengeResponseSubmissionsResult
  >,
  'getRoundRobinCanister' : ActorMethod<[], CanisterIDRecordResult>,
  'getShareServiceCanisterId' : ActorMethod<[], string>,
  'getSubmittedResponsesAdmin' : ActorMethod<
    [],
    ChallengeResponseSubmissionsResult
  >,
  'health' : ActorMethod<[], StatusCodeRecordResult>,
  'ready' : ActorMethod<[], StatusCodeRecordResult>,
  'reset_llm_canisters' : ActorMethod<[], StatusCodeRecordResult>,
  'setGameStateCanisterId' : ActorMethod<[string], StatusCodeRecordResult>,
  'setMainerCanisterType' : ActorMethod<
    [MainerAgentCanisterType],
    StatusCodeRecordResult
  >,
  'setRoundRobinLLMs' : ActorMethod<[bigint], StatusCodeRecordResult>,
  'setShareServiceCanisterId' : ActorMethod<[string], StatusCodeRecordResult>,
  'startTimerExecutionAdmin' : ActorMethod<[], AuthRecordResult>,
  'stopTimerExecutionAdmin' : ActorMethod<[], AuthRecordResult>,
  'triggerChallengeResponseAdmin' : ActorMethod<[], AuthRecordResult>,
  'updateAgentSettings' : ActorMethod<
    [MainerAgentSettingsInput],
    StatusCodeRecordResult
  >,
  'whoami' : ActorMethod<[], Principal>,
}
export interface MainerAgentSettingsInput {
  'cyclesBurnRate' : CyclesBurnRateDefault,
}
export interface MainerConfigurationInput {
  'selectedLLM' : [] | [SelectableMainerLLMs],
  'mainerAgentCanisterType' : MainerAgentCanisterType,
}
export interface OfficialMainerAgentCanister {
  'status' : CanisterStatus,
  'canisterType' : ProtocolCanisterType,
  'ownedBy' : Principal,
  'creationTimestamp' : bigint,
  'createdBy' : Principal,
  'mainerConfig' : MainerConfigurationInput,
  'address' : CanisterAddress,
}
export type ProtocolCanisterType = { 'MainerAgent' : MainerAgentCanisterType } |
  { 'MainerLlm' : null } |
  { 'Challenger' : null } |
  { 'Judge' : null } |
  { 'Verifier' : null } |
  { 'MainerCreator' : null };
export type SelectableMainerLLMs = { 'Qwen2_5_500M' : null };
export interface StatisticsRecord {
  'cycleBalance' : bigint,
  'totalCyclesBurnt' : bigint,
  'cyclesBurnRate' : CyclesBurnRate,
}
export type StatisticsRetrievalResult = { 'Ok' : StatisticsRecord } |
  { 'Err' : ApiError };
export type StatusCode = number;
export interface StatusCodeRecord { 'status_code' : StatusCode }
export type StatusCodeRecordResult = { 'Ok' : StatusCodeRecord } |
  { 'Err' : ApiError };
export type TimeInterval = { 'Daily' : null };
export interface _SERVICE extends MainerAgentCtrlbCanister {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
