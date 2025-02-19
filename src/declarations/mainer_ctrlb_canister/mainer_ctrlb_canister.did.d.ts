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
export interface CanisterIDRecord { 'canister_id' : string }
export type CanisterIDRecordResult = { 'Ok' : CanisterIDRecord } |
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
  'challengeTopic' : string,
  'submissionId' : string,
  'challengeAnswerSeed' : number,
  'submissionCyclesRequired' : bigint,
  'challengeAnswer' : string,
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
export interface MainerAgentCtrlbCanister {
  'add_llm_canister' : ActorMethod<[CanisterIDRecord], StatusCodeRecordResult>,
  'amiController' : ActorMethod<[], StatusCodeRecordResult>,
  'checkAccessToLLMs' : ActorMethod<[], StatusCodeRecordResult>,
  'getGameStateCanisterId' : ActorMethod<[], string>,
  'getRoundRobinCanister' : ActorMethod<[], CanisterIDRecordResult>,
  'getSubmittedResponsesAdmin' : ActorMethod<
    [],
    ChallengeResponseSubmissionsResult
  >,
  'health' : ActorMethod<[], StatusCodeRecordResult>,
  'ready' : ActorMethod<[], StatusCodeRecordResult>,
  'reset_llm_canisters' : ActorMethod<[], StatusCodeRecordResult>,
  'setGameStateCanisterId' : ActorMethod<[string], StatusCodeRecordResult>,
  'setRoundRobinLLMs' : ActorMethod<[bigint], StatusCodeRecordResult>,
  'startTimerExecutionAdmin' : ActorMethod<[], AuthRecordResult>,
  'stopTimerExecutionAdmin' : ActorMethod<[], AuthRecordResult>,
  'triggerChallengeResponseAdmin' : ActorMethod<[], AuthRecordResult>,
  'updateAgentSettings' : ActorMethod<
    [MainerAgentSettingsInput],
    StatusCodeRecordResult
  >,
  'whoami' : ActorMethod<[], Principal>,
}
export interface MainerAgentSettingsInput { 'cyclesBurnRate' : CyclesBurnRate }
export type StatusCode = number;
export interface StatusCodeRecord { 'status_code' : StatusCode }
export type StatusCodeRecordResult = { 'Ok' : StatusCodeRecord } |
  { 'Err' : ApiError };
export type TimeInterval = { 'Daily' : null };
export interface _SERVICE extends MainerAgentCtrlbCanister {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
