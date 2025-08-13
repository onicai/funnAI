export const idlFactory = ({ IDL }) => {
  const MaxMainerTopUpInput = IDL.Record({
    'paymentTransactionBlockId' : IDL.Nat64,
    'toppedUpMainerId' : IDL.Text,
    'amount' : IDL.Nat,
  });
  const MaxMainerTopUpStorageResponse = IDL.Record({ 'stored' : IDL.Bool });
  const ApiError = IDL.Variant({
    'InvalidId' : IDL.Null,
    'ZeroAddress' : IDL.Null,
    'Unauthorized' : IDL.Null,
    'Other' : IDL.Text,
  });
  const MaxMainerTopUpStorageResult = IDL.Variant({
    'Ok' : MaxMainerTopUpStorageResponse,
    'Err' : ApiError,
  });
  const BoolResult = IDL.Variant({ 'Ok' : IDL.Bool, 'Err' : ApiError });
  const Message = IDL.Record({ 'content' : IDL.Text, 'sender' : IDL.Text });
  const ChatCreationResult = IDL.Variant({ 'Ok' : IDL.Text, 'Err' : ApiError });
  const Chat = IDL.Record({
    'id' : IDL.Text,
    'messages' : IDL.Vec(Message),
    'owner' : IDL.Principal,
    'creationTime' : IDL.Nat64,
    'chatTitle' : IDL.Text,
    'firstMessagePreview' : IDL.Text,
  });
  const ChatResult = IDL.Variant({ 'Ok' : Chat, 'Err' : ApiError });
  const TopUpRecord = IDL.Record({
    'paymentTransactionBlockId' : IDL.Nat64,
    'toppedUpMainerId' : IDL.Text,
    'timestamp' : IDL.Nat64,
    'caller' : IDL.Text,
    'amount' : IDL.Nat,
  });
  const MaxMainerTopUpsResult = IDL.Variant({
    'Ok' : IDL.Vec(TopUpRecord),
    'Err' : ApiError,
  });
  const LoginEvent = IDL.Record({
    'principal' : IDL.Text,
    'timestamp' : IDL.Nat64,
  });
  const LoginEventsResult = IDL.Variant({
    'Ok' : IDL.Vec(LoginEvent),
    'Err' : ApiError,
  });
  const NatResult = IDL.Variant({ 'Ok' : IDL.Nat, 'Err' : ApiError });
  const GetUsersResult = IDL.Variant({
    'Ok' : IDL.Vec(IDL.Text),
    'Err' : ApiError,
  });
  const ChatPreview = IDL.Record({
    'id' : IDL.Text,
    'creationTime' : IDL.Nat64,
    'chatTitle' : IDL.Text,
    'firstMessagePreview' : IDL.Text,
  });
  const ChatsPreviewResult = IDL.Variant({
    'Ok' : IDL.Vec(ChatPreview),
    'Err' : ApiError,
  });
  const UserChatSettings = IDL.Record({
    'responseLength' : IDL.Text,
    'temperature' : IDL.Float64,
    'selectedAiModelId' : IDL.Text,
    'systemPrompt' : IDL.Text,
    'saveChats' : IDL.Bool,
  });
  const UserChatSettingsResult = IDL.Variant({
    'Ok' : UserChatSettings,
    'Err' : ApiError,
  });
  const ChatsResult = IDL.Variant({ 'Ok' : IDL.Vec(Chat), 'Err' : ApiError });
  const UserInfo = IDL.Record({
    'createdAt' : IDL.Nat64,
    'isPremiumAccount' : IDL.Bool,
    'emailAddress' : IDL.Opt(IDL.Text),
  });
  const UserInfoResult = IDL.Variant({ 'Ok' : UserInfo, 'Err' : ApiError });
  const EmailSubscriber = IDL.Record({
    'subscribedAt' : IDL.Nat64,
    'emailAddress' : IDL.Text,
    'pageSubmittedFrom' : IDL.Text,
  });
  const UpdateUserInfoResult = IDL.Variant({
    'Ok' : IDL.Bool,
    'Err' : ApiError,
  });
  const PaymentInfoInput = IDL.Record({ 'block_index' : IDL.Nat64 });
  const SignUpFormInput = IDL.Record({
    'emailAddress' : IDL.Text,
    'pageSubmittedFrom' : IDL.Text,
  });
  const UpdateUserChatSettingsResult = IDL.Variant({
    'Ok' : IDL.Bool,
    'Err' : ApiError,
  });
  const UserInfoInput = IDL.Record({ 'emailAddress' : IDL.Opt(IDL.Text) });
  const ChatIdResult = IDL.Variant({ 'Ok' : IDL.Text, 'Err' : ApiError });
  const UpdateChatObject = IDL.Record({
    'id' : IDL.Text,
    'chatTitle' : IDL.Text,
  });
  const FunnAIBackend = IDL.Service({
    'addMaxMainerTopup' : IDL.Func(
        [MaxMainerTopUpInput],
        [MaxMainerTopUpStorageResult],
        [],
      ),
    'archiveMaxMainerTopupsAdmin' : IDL.Func([], [BoolResult], []),
    'create_chat' : IDL.Func([IDL.Vec(Message)], [ChatCreationResult], []),
    'delete_chat' : IDL.Func([IDL.Text], [ChatResult], []),
    'delete_email_subscriber' : IDL.Func([IDL.Text], [IDL.Bool], []),
    'getArchivedMaxMainerTopupsAdmin' : IDL.Func(
        [],
        [MaxMainerTopUpsResult],
        ['query'],
      ),
    'getLoginEventsAdmin' : IDL.Func(
        [IDL.Text],
        [LoginEventsResult],
        ['query'],
      ),
    'getMaxMainerTopupsAdmin' : IDL.Func(
        [],
        [MaxMainerTopUpsResult],
        ['query'],
      ),
    'getNumArchivedMaxMainerTopupsAdmin' : IDL.Func([], [NatResult], ['query']),
    'getUsersAdmin' : IDL.Func([], [GetUsersResult], ['query']),
    'get_caller_chat_history' : IDL.Func([], [ChatsPreviewResult], ['query']),
    'get_caller_chat_settings' : IDL.Func(
        [],
        [UserChatSettingsResult],
        ['query'],
      ),
    'get_caller_chats' : IDL.Func([], [ChatsResult], ['query']),
    'get_caller_user_info' : IDL.Func([], [UserInfoResult], ['query']),
    'get_chat' : IDL.Func([IDL.Text], [ChatResult], ['query']),
    'get_email_subscribers' : IDL.Func(
        [],
        [IDL.Vec(IDL.Tuple(IDL.Text, EmailSubscriber))],
        ['query'],
      ),
    'get_user_info_admin' : IDL.Func([IDL.Text], [UserInfoResult], ['query']),
    'logLogin' : IDL.Func([], [UpdateUserInfoResult], []),
    'make_caller_account_premium' : IDL.Func(
        [PaymentInfoInput],
        [UpdateUserInfoResult],
        [],
      ),
    'submit_signup_form' : IDL.Func([SignUpFormInput], [IDL.Text], []),
    'update_caller_chat_settings' : IDL.Func(
        [UserChatSettings],
        [UpdateUserChatSettingsResult],
        [],
      ),
    'update_caller_user_info' : IDL.Func(
        [UserInfoInput],
        [UpdateUserInfoResult],
        [],
      ),
    'update_chat_messages' : IDL.Func(
        [IDL.Text, IDL.Vec(Message)],
        [ChatIdResult],
        [],
      ),
    'update_chat_metadata' : IDL.Func([UpdateChatObject], [ChatIdResult], []),
  });
  return FunnAIBackend;
};
export const init = ({ IDL }) => { return [IDL.Principal]; };
