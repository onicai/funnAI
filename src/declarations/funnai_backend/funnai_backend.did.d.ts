import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export type ApiError = { 'InvalidId' : null } |
  { 'ZeroAddress' : null } |
  { 'Unauthorized' : null } |
  { 'Other' : string };
export interface Chat {
  'id' : string,
  'messages' : Array<Message>,
  'owner' : Principal,
  'creationTime' : bigint,
  'chatTitle' : string,
  'firstMessagePreview' : string,
}
export type ChatCreationResult = { 'Ok' : string } |
  { 'Err' : ApiError };
export type ChatIdResult = { 'Ok' : string } |
  { 'Err' : ApiError };
export interface ChatPreview {
  'id' : string,
  'creationTime' : bigint,
  'chatTitle' : string,
  'firstMessagePreview' : string,
}
export type ChatResult = { 'Ok' : Chat } |
  { 'Err' : ApiError };
export type ChatsPreviewResult = { 'Ok' : Array<ChatPreview> } |
  { 'Err' : ApiError };
export type ChatsResult = { 'Ok' : Array<Chat> } |
  { 'Err' : ApiError };
export interface EmailSubscriber {
  'subscribedAt' : bigint,
  'emailAddress' : string,
  'pageSubmittedFrom' : string,
}
export interface FunnAIBackend {
  'addMaxMainerTopup' : ActorMethod<
    [MaxMainerTopUpInput],
    MaxMainerTopUpStorageResult
  >,
  'create_chat' : ActorMethod<[Array<Message>], ChatCreationResult>,
  'delete_chat' : ActorMethod<[string], ChatResult>,
  'delete_email_subscriber' : ActorMethod<[string], boolean>,
  'getLoginEventsAdmin' : ActorMethod<[string], LoginEventsResult>,
  'getMaxMainerTopupsAdmin' : ActorMethod<[], MaxMainerTopUpsResult>,
  'get_caller_chat_history' : ActorMethod<[], ChatsPreviewResult>,
  'get_caller_chat_settings' : ActorMethod<[], UserChatSettingsResult>,
  'get_caller_chats' : ActorMethod<[], ChatsResult>,
  'get_caller_user_info' : ActorMethod<[], UserInfoResult>,
  'get_chat' : ActorMethod<[string], ChatResult>,
  'get_email_subscribers' : ActorMethod<[], Array<[string, EmailSubscriber]>>,
  'get_user_info_admin' : ActorMethod<[string], UserInfoResult>,
  'logLogin' : ActorMethod<[], UpdateUserInfoResult>,
  'make_caller_account_premium' : ActorMethod<
    [PaymentInfoInput],
    UpdateUserInfoResult
  >,
  'submit_signup_form' : ActorMethod<[SignUpFormInput], string>,
  'update_caller_chat_settings' : ActorMethod<
    [UserChatSettings],
    UpdateUserChatSettingsResult
  >,
  'update_caller_user_info' : ActorMethod<
    [UserInfoInput],
    UpdateUserInfoResult
  >,
  'update_chat_messages' : ActorMethod<[string, Array<Message>], ChatIdResult>,
  'update_chat_metadata' : ActorMethod<[UpdateChatObject], ChatIdResult>,
}
export interface LoginEvent { 'principal' : string, 'timestamp' : bigint }
export type LoginEventsResult = { 'Ok' : Array<LoginEvent> } |
  { 'Err' : ApiError };
export interface MaxMainerTopUpInput {
  'paymentTransactionBlockId' : bigint,
  'toppedUpMainerId' : string,
  'amount' : bigint,
}
export interface MaxMainerTopUpStorageResponse { 'stored' : boolean }
export type MaxMainerTopUpStorageResult = {
    'Ok' : MaxMainerTopUpStorageResponse
  } |
  { 'Err' : ApiError };
export type MaxMainerTopUpsResult = { 'Ok' : Array<TopUpRecord> } |
  { 'Err' : ApiError };
export interface Message { 'content' : string, 'sender' : string }
export interface PaymentInfoInput { 'block_index' : bigint }
export interface SignUpFormInput {
  'emailAddress' : string,
  'pageSubmittedFrom' : string,
}
export interface TopUpRecord {
  'paymentTransactionBlockId' : bigint,
  'toppedUpMainerId' : string,
  'timestamp' : bigint,
  'caller' : string,
  'amount' : bigint,
}
export interface UpdateChatObject { 'id' : string, 'chatTitle' : string }
export type UpdateUserChatSettingsResult = { 'Ok' : boolean } |
  { 'Err' : ApiError };
export type UpdateUserInfoResult = { 'Ok' : boolean } |
  { 'Err' : ApiError };
export interface UserChatSettings {
  'responseLength' : string,
  'temperature' : number,
  'selectedAiModelId' : string,
  'systemPrompt' : string,
  'saveChats' : boolean,
}
export type UserChatSettingsResult = { 'Ok' : UserChatSettings } |
  { 'Err' : ApiError };
export interface UserInfo {
  'createdAt' : bigint,
  'isPremiumAccount' : boolean,
  'emailAddress' : [] | [string],
}
export interface UserInfoInput { 'emailAddress' : [] | [string] }
export type UserInfoResult = { 'Ok' : UserInfo } |
  { 'Err' : ApiError };
export interface _SERVICE extends FunnAIBackend {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
