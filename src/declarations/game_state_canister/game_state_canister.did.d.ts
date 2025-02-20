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
  'address' : CanisterAddress,
}
export interface CanisterRetrieveInput { 'address' : CanisterAddress }
export interface Challenge {
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
  'challengeTopic' : string,
  'submissionCyclesRequired' : bigint,
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
  'challengeTopic' : string,
  'challengeAnswerSeed' : number,
  'submissionCyclesRequired' : bigint,
  'challengeAnswer' : string,
}
export interface ChallengeResponseSubmissionMetadata {
  'submittedTimestamp' : bigint,
  'submissionStatus' : ChallengeResponseSubmissionStatus,
  'submissionId' : string,
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
export type CyclesBurntResult = { 'Ok' : bigint } |
  { 'Err' : ApiError };
export interface GameStateCanister {
  'addChallenge' : ActorMethod<[NewChallengeInput], ChallengeAdditionResult>,
  'addChallengeTopic' : ActorMethod<
    [ChallengeTopicInput],
    ChallengeTopicResult
  >,
  'addMainerAgentCanister' : ActorMethod<
    [MainerAgentCanisterInput],
    MainerAgentCanisterResult
  >,
  'addMainerAgentCanisterAdmin' : ActorMethod<
    [MainerAgentCanisterInput],
    MainerAgentCanisterResult
  >,
  'addOfficialCanister' : ActorMethod<[CanisterInput], StatusCodeRecordResult>,
  'addScoredResponse' : ActorMethod<
    [ScoredResponseInput],
    ScoredResponseResult
  >,
  'createUserMainerAgentCanister' : ActorMethod<
    [MainerConfigurationInput],
    MainerAgentCanisterResult
  >,
  'getCurrentChallenges' : ActorMethod<[], ChallengesResult>,
  'getCurrentChallengesAdmin' : ActorMethod<[], ChallengesResult>,
  'getMainerAgentCanisterInfo' : ActorMethod<
    [CanisterRetrieveInput],
    MainerAgentCanisterResult
  >,
  'getMainerAgentCanistersForUser' : ActorMethod<
    [],
    MainerAgentCanistersResult
  >,
  'getNextSubmissionToJudge' : ActorMethod<
    [],
    ChallengeResponseSubmissionResult
  >,
  'getOfficialChallengerCanisters' : ActorMethod<[], AuthRecordResult>,
  'getProtocolTotalCyclesBurnt' : ActorMethod<[], CyclesBurntResult>,
  'getRandomOpenChallenge' : ActorMethod<[], ChallengeResult>,
  'getRandomOpenChallengeTopic' : ActorMethod<[], ChallengeTopicResult>,
  'getRecentChallengeWinners' : ActorMethod<[], ChallengeWinnersResult>,
  'getRecentProtocolActivity' : ActorMethod<[], ProtocolActivityResult>,
  'getScoreForSubmission' : ActorMethod<
    [SubmissionRetrievalInput],
    ScoredResponseRetrievalResult
  >,
  'getScoredChallengesAdmin' : ActorMethod<[], ScoredChallengesResult>,
  'getSubmissionsAdmin' : ActorMethod<[], ChallengeResponseSubmissionsResult>,
  'health' : ActorMethod<[], StatusCodeRecordResult>,
  'setInitialChallengeTopics' : ActorMethod<[], StatusCodeRecordResult>,
  'submitChallengeResponse' : ActorMethod<
    [ChallengeResponseSubmissionInput],
    ChallengeResponseSubmissionMetadataResult
  >,
}
export type List = [] | [[ScoredResponse, List]];
export type List_1 = [] | [[ChallengeParticipantEntry, List_1]];
export interface MainerAgentCanisterInput {
  'canisterType' : ProtocolCanisterType,
  'ownedBy' : Principal,
  'address' : CanisterAddress,
}
export type MainerAgentCanisterResult = { 'Ok' : OfficialProtocolCanister } |
  { 'Err' : ApiError };
export type MainerAgentCanistersResult = {
    'Ok' : Array<OfficialProtocolCanister>
  } |
  { 'Err' : ApiError };
export interface MainerConfigurationInput {
  'aiModel' : [] | [SelectableMainerLLM],
}
export interface NewChallengeInput {
  'challengeTopicStatus' : ChallengeTopicStatus,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeTopicId' : string,
  'challengeQuestionSeed' : number,
  'challengeQuestion' : string,
  'challengeTopic' : string,
}
export interface OfficialProtocolCanister {
  'canisterType' : ProtocolCanisterType,
  'ownedBy' : Principal,
  'creationTimestamp' : bigint,
  'createdBy' : Principal,
  'address' : CanisterAddress,
}
export interface ProtocolActivityRecord {
  'challenges' : Array<Challenge>,
  'winners' : Array<ChallengeWinnerDeclaration>,
}
export type ProtocolActivityResult = { 'Ok' : ProtocolActivityRecord } |
  { 'Err' : ApiError };
export type ProtocolCanisterType = { 'MainerAgent' : null } |
  { 'Challenger' : null } |
  { 'Judge' : null } |
  { 'Verifier' : null } |
  { 'MainerCreator' : null };
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
  'challengeTopicCreationTimestamp' : bigint,
  'challengeCreationTimestamp' : bigint,
  'challengeCreatedBy' : CanisterAddress,
  'challengeTopicId' : string,
  'judgedBy' : Principal,
  'submittedTimestamp' : bigint,
  'submittedBy' : Principal,
  'challengeStatus' : ChallengeStatus,
  'challengeQuestionSeed' : number,
  'submissionStatus' : ChallengeResponseSubmissionStatus,
  'score' : bigint,
  'challengeQuestion' : string,
  'challengeId' : string,
  'challengeTopic' : string,
  'judgedTimestamp' : bigint,
  'submissionId' : string,
  'challengeAnswerSeed' : number,
  'submissionCyclesRequired' : bigint,
  'challengeAnswer' : string,
  'scoreSeed' : number,
}
export interface ScoredResponseInput {
  'challengeClosedTimestamp' : [] | [bigint],
  'challengeTopicStatus' : ChallengeTopicStatus,
  'challengeTopicCreationTimestamp' : bigint,
  'challengeCreationTimestamp' : bigint,
  'challengeCreatedBy' : CanisterAddress,
  'challengeTopicId' : string,
  'judgedBy' : Principal,
  'submittedTimestamp' : bigint,
  'submittedBy' : Principal,
  'challengeStatus' : ChallengeStatus,
  'challengeQuestionSeed' : number,
  'submissionStatus' : ChallengeResponseSubmissionStatus,
  'score' : bigint,
  'challengeQuestion' : string,
  'challengeId' : string,
  'challengeTopic' : string,
  'submissionId' : string,
  'challengeAnswerSeed' : number,
  'submissionCyclesRequired' : bigint,
  'challengeAnswer' : string,
  'scoreSeed' : number,
}
export type ScoredResponseResult = { 'Ok' : ScoredResponseReturn } |
  { 'Err' : ApiError };
export type ScoredResponseRetrievalResult = { 'Ok' : ScoredResponse } |
  { 'Err' : ApiError };
export interface ScoredResponseReturn { 'success' : boolean }
export type SelectableMainerLLM = { 'Qwen2_5_0_5_B' : null };
export type StatusCode = number;
export interface StatusCodeRecord { 'status_code' : StatusCode }
export type StatusCodeRecordResult = { 'Ok' : StatusCodeRecord } |
  { 'Err' : ApiError };
export interface SubmissionRetrievalInput {
  'challengeId' : string,
  'submissionId' : string,
}
export interface _SERVICE extends GameStateCanister {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
