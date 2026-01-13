import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export interface AddCyclesRecord { 'added' : boolean, 'amount' : bigint }
export type AddCyclesResult = { 'Ok' : AddCyclesRecord } |
  { 'Err' : ApiError };
export type AdminRole = { 'AdminQuery' : null } |
  { 'AdminUpdate' : null };
export interface AdminRoleAssignment {
  'principal' : string,
  'assignedAt' : bigint,
  'assignedBy' : string,
  'note' : string,
  'role' : AdminRole,
}
export type AdminRoleAssignmentResult = { 'Ok' : AdminRoleAssignment } |
  { 'Err' : ApiError };
export type AdminRoleAssignmentsResult = { 'Ok' : Array<AdminRoleAssignment> } |
  { 'Err' : ApiError };
export type ApiError = { 'FailedOperation' : null } |
  { 'InvalidId' : null } |
  { 'ZeroAddress' : null } |
  { 'Unauthorized' : null } |
  { 'StatusCode' : StatusCode } |
  { 'Other' : string } |
  { 'InsuffientCycles' : bigint };
export interface AssignAdminRoleInputRecord {
  'principal' : string,
  'note' : string,
  'role' : AdminRole,
}
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
  'challengeQueuedBy' : Principal,
  'challengeQueuedId' : string,
  'challengeQueuedTo' : Principal,
  'challengeTopic' : string,
  'cyclesGenerateChallengeChctrlChllm' : bigint,
  'cyclesGenerateResponseSactrlSsctrl' : bigint,
  'judgePromptId' : string,
  'challengeQueuedTimestamp' : bigint,
  'cyclesSubmitResponse' : bigint,
  'cyclesGenerateChallengeGsChctrl' : bigint,
  'cyclesGenerateResponseSsctrlGs' : bigint,
}
export type ChallengeQueueInputResult = { 'Ok' : ChallengeQueueInput } |
  { 'Err' : ApiError };
export type ChallengeQueueInputsResult = { 'Ok' : Array<ChallengeQueueInput> } |
  { 'Err' : ApiError };
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
export interface FlagRecord { 'flag' : boolean }
export type FlagResult = { 'Ok' : FlagRecord } |
  { 'Err' : ApiError };
export interface IssueFlagsRecord { 'lowCycleBalance' : boolean }
export type IssueFlagsRetrievalResult = { 'Ok' : IssueFlagsRecord } |
  { 'Err' : ApiError };
export interface LlmCanistersRecord {
  'roundRobinUseAll' : boolean,
  'roundRobinLLMs' : bigint,
  'llmCanisterIds' : Array<CanisterAddress>,
}
export type LlmCanistersRecordResult = { 'Ok' : LlmCanistersRecord } |
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
  'assignAdminRole' : ActorMethod<
    [AssignAdminRoleInputRecord],
    AdminRoleAssignmentResult
  >,
  'canAgentSettingsBeUpdated' : ActorMethod<[], StatusCodeRecordResult>,
  'checkAccessToLLMs' : ActorMethod<[], StatusCodeRecordResult>,
  'getAdminRoles' : ActorMethod<[], AdminRoleAssignmentsResult>,
  'getAgentSettingsAdmin' : ActorMethod<[], MainerAgentSettingsListResult>,
  'getAgentTimersAdmin' : ActorMethod<[], MainerAgentTimersListResult>,
  'getChallengeQueueAdmin' : ActorMethod<[], ChallengeQueueInputsResult>,
  'getCurrentAgentSettingsAdmin' : ActorMethod<[], MainerAgentSettingsResult>,
  'getCurrentAgentTimersAdmin' : ActorMethod<[], MainerAgentTimersResult>,
  'getGameStateCanisterId' : ActorMethod<[], string>,
  'getIssueFlagsAdmin' : ActorMethod<[], IssueFlagsRetrievalResult>,
  'getLLMCanisterIds' : ActorMethod<[], CanisterAddressesResult>,
  'getMainerCanisterType' : ActorMethod<[], MainerAgentCanisterTypeResult>,
  'getMainerStatisticsAdmin' : ActorMethod<[], StatisticsRetrievalResult>,
  'getMaintenanceFlag' : ActorMethod<[], FlagResult>,
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
  'getTimerActionRegularityInSecondsAdmin' : ActorMethod<
    [],
    MainerTimersResult
  >,
  'getTimerBufferMaxSizeAdmin' : ActorMethod<[], NatResult>,
  'getTimerBuffersAdmin' : ActorMethod<[], MainerTimerBuffersResult>,
  'get_llm_canisters' : ActorMethod<[], LlmCanistersRecordResult>,
  'health' : ActorMethod<[], StatusCodeRecordResult>,
  'ready' : ActorMethod<[], StatusCodeRecordResult>,
  'remove_llm_canister' : ActorMethod<
    [CanisterIDRecord],
    StatusCodeRecordResult
  >,
  'resetChallengeQueueAdmin' : ActorMethod<[], StatusCodeRecordResult>,
  'resetRoundRobinLLMs' : ActorMethod<[], StatusCodeRecordResult>,
  'reset_llm_canisters' : ActorMethod<[], StatusCodeRecordResult>,
  'revokeAdminRole' : ActorMethod<[string], TextResult>,
  'setGameStateCanisterId' : ActorMethod<[string], StatusCodeRecordResult>,
  'setMainerCanisterType' : ActorMethod<
    [MainerAgentCanisterType],
    StatusCodeRecordResult
  >,
  'setRoundRobinLLMs' : ActorMethod<[bigint], StatusCodeRecordResult>,
  'setShareServiceCanisterId' : ActorMethod<[string], StatusCodeRecordResult>,
  'setTimerAction2RegularityInSecondsAdmin' : ActorMethod<
    [bigint],
    StatusCodeRecordResult
  >,
  'setTimerBufferMaxSizeAdmin' : ActorMethod<[bigint], StatusCodeRecordResult>,
  'startTimerExecutionAdmin' : ActorMethod<[], AuthRecordResult>,
  'stopTimerExecutionAdmin' : ActorMethod<[], AuthRecordResult>,
  'timeToNextAgentSettingsUpdate' : ActorMethod<[], NatResult>,
  'toggleMaintenanceFlagAdmin' : ActorMethod<[], AuthRecordResult>,
  'triggerChallengeResponseAdmin' : ActorMethod<[], AuthRecordResult>,
  'updateAgentSettings' : ActorMethod<
    [MainerAgentSettingsInput],
    StatusCodeRecordResult
  >,
  'whoami' : ActorMethod<[], Principal>,
}
export interface MainerAgentSettings {
  'creationTimestamp' : bigint,
  'createdBy' : Principal,
  'cyclesBurnRate' : CyclesBurnRateDefault,
}
export interface MainerAgentSettingsInput {
  'cyclesBurnRate' : CyclesBurnRateDefault,
}
export type MainerAgentSettingsListResult = {
    'Ok' : Array<MainerAgentSettings>
  } |
  { 'Err' : ApiError };
export type MainerAgentSettingsResult = { 'Ok' : MainerAgentSettings } |
  { 'Err' : ApiError };
export interface MainerAgentTimers {
  'recurringTimerId1' : [] | [bigint],
  'recurringTimerId2' : [] | [bigint],
  'randomInitialTimer1InSeconds' : [] | [bigint],
  'creationTimestamp' : bigint,
  'calledFromEndpoint' : string,
  'createdBy' : Principal,
  'action2RegularityInSeconds' : bigint,
  'initialTimerId1' : [] | [bigint],
  'action1RegularityInSeconds' : bigint,
}
export type MainerAgentTimersListResult = { 'Ok' : Array<MainerAgentTimers> } |
  { 'Err' : ApiError };
export type MainerAgentTimersResult = { 'Ok' : MainerAgentTimers } |
  { 'Err' : ApiError };
export interface MainerConfigurationInput {
  'selectedLLM' : [] | [SelectableMainerLLMs],
  'subnetLlm' : string,
  'mainerAgentCanisterType' : MainerAgentCanisterType,
  'cyclesForMainer' : bigint,
  'subnetCtrl' : string,
}
export interface MainerTimerBuffers {
  'bufferTimerId1' : Array<bigint>,
  'bufferTimerId2' : Array<bigint>,
}
export type MainerTimerBuffersResult = { 'Ok' : MainerTimerBuffers } |
  { 'Err' : ApiError };
export interface MainerTimers {
  'action2RegularityInSeconds' : bigint,
  'action1RegularityInSeconds' : bigint,
}
export type MainerTimersResult = { 'Ok' : MainerTimers } |
  { 'Err' : ApiError };
export type NatResult = { 'Ok' : bigint } |
  { 'Err' : ApiError };
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
export type TextResult = { 'Ok' : string } |
  { 'Err' : ApiError };
export type TimeInterval = { 'Daily' : null };
export interface _SERVICE extends MainerAgentCtrlbCanister {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
