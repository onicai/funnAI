import List "mo:base/List";
import Principal "mo:base/Principal";
import Text "mo:base/Text";
import Iter "mo:base/Iter";
import Nat64 "mo:base/Nat64";
import Time "mo:base/Time";
import Int "mo:base/Int";
import HashMap "mo:base/HashMap";
import Array "mo:base/Array";

import Utils "./Utils";

import Types "./Types";

shared actor class FunnAIBackend(custodian: Principal) = Self {
  stable var custodians = List.make<Principal>(custodian);

  // https://forum.dfinity.org/t/is-there-any-address-0-equivalent-at-dfinity-motoko/5445/3
  let null_address : Principal = Principal.fromText("aaaaa-aa");

// Project-specific functions
  stable var userChatsStorageStable : [(Principal, List.List<Text>)] = [];
  var userChatsStorage : HashMap.HashMap<Principal, List.List<Text>> = HashMap.HashMap(0, Principal.equal, Principal.hash);
  stable var userChatSettingsStorageStable : [(Principal, Types.UserChatSettings)] = [];
  var userChatSettingsStorage : HashMap.HashMap<Principal, Types.UserChatSettings> = HashMap.HashMap(0, Principal.equal, Principal.hash);
  stable var chatsStorageStable : [(Text, Types.Chat)] = [];
  var chatsStorage : HashMap.HashMap<Text, Types.Chat> = HashMap.HashMap(0, Text.equal, Text.hash);

  stable var userInfoStorageStable : [(Principal, Types.UserInfo)] = [];
  var userInfoStorage : HashMap.HashMap<Principal, Types.UserInfo> = HashMap.HashMap(0, Principal.equal, Principal.hash);

  /**
   * Simple function to store a chat in the database. There are no protections so this function should only
   * be called if the caller has permissions to store the chat to the database
   *
   * @return The chat id of the stored chat
  */
  private func putChat(chat : Types.Chat) : Text {
    chatsStorage.put(chat.id, chat);
    return chat.id;
  };

  /**
   * A simple function to retrieve a chat by the chat id, this provides no protection so should only be called if
   * the caller has permissions to read the chat data
   *
   * @return The chat if it exists, otherwise null
  */
  private func getChat(chatId : Text) : ?Types.Chat {
    let result = chatsStorage.get(chatId);
    return result;
  };

  /**
   * Simple function to store a chat for the user in the database. There are no protections so this function should only
   * be called if the caller has permissions to store the chat to the database
   *
   * @return The chat id of the stored chat
  */
  private func putUserChat(user : Principal, chatId : Text) : Text {
    let userChatIds : List.List<Text> = getUserChatIds(user);
    let updatedChatIds = List.push<Text>(chatId, userChatIds);
    userChatsStorage.put(user, updatedChatIds);
    return chatId;
  };

  /**
   * A simple function to retrieve the user's chat, this provides no protection so should only be called if
   * the caller has permissions to read the chat data
   *
   * @return The user's chats if at least one exists, otherwise an empty List
  */
  private func getUserChats(user : Principal) : List.List<Types.Chat> {
    let userChatIds : List.List<Text> = getUserChatIds(user);
    var userChats : List.List<Types.Chat> = List.nil<Types.Chat>();
    for (chatId in List.toArray<Text>(userChatIds).vals()) {
      let chat = getChat(chatId);
      switch (chat) {
        case (null) {};
        case (?chat) { userChats := List.push<Types.Chat>(chat, userChats); };
      };
    };
    return userChats;
  };

  private func getUserChatIds(user : Principal) : List.List<Text> {
    let userChatIds : ?List.List<Text> = userChatsStorage.get(user);
    switch (userChatIds) {
      case (null) { return List.nil<Text>(); };
      case (?userChatIds) { return userChatIds; };
    };
  };

  private func deleteChat(chatId : Text) : Text {
    chatsStorage.delete(chatId);
    return chatId;
  };

  private func deleteUserChat(user : Principal, chatId : Text) : Text {
    let userChatIds : List.List<Text> = getUserChatIds(user);
    let updatedChatIds = List.filter(userChatIds, func(id: Text) : Bool { id != chatId });
    userChatsStorage.put(user, updatedChatIds);
    return chatId;
  };

  public shared({ caller }) func create_chat(messages : [Types.Message]) : async Types.ChatCreationResult {
    // disabled
    return #Err(#Unauthorized);
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    let newId : Text = await Utils.newRandomUniqueId();

    var firstMessagePreview : Text = "";
    if (messages.size() > 0) {
      firstMessagePreview := messages[0].content;
    };

    let newChat : Types.Chat = {
      id : Text = newId;
      messages : [Types.Message] = messages;
      owner : Principal = caller;
      creationTime : Nat64 = Nat64.fromNat(Int.abs(Time.now()));
      firstMessagePreview : Text = firstMessagePreview;
      chatTitle : Text = "";
    };

    let chatCreated = putChat(newChat);
    let result = putUserChat(caller, newId);

    return #Ok(result);
  };

  public shared query ({caller}) func get_caller_chats() : async Types.ChatsResult {
    // don't allow anonymous Principal
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    let chats = getUserChats(caller);
    return #Ok(List.toArray(chats)); 
  };

  public shared query ({caller}) func get_caller_chat_history() : async Types.ChatsPreviewResult {
    // don't allow anonymous Principal
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    let chats = getUserChats(caller);
    var chatsPreview : List.List<Types.ChatPreview> = List.nil<Types.ChatPreview>();
    chatsPreview := List.map<Types.Chat, Types.ChatPreview>(chats, func (chat : Types.Chat) : Types.ChatPreview {
      return {
        id : Text = chat.id;
        creationTime : Nat64 = chat.creationTime;
        firstMessagePreview : Text = chat.firstMessagePreview;
        chatTitle : Text = chat.chatTitle;
      };
    });
    return #Ok(List.toArray(chatsPreview)); 
  };

  public shared query ({caller}) func get_chat(chatId : Text) : async Types.ChatResult {
    // don't allow anonymous Principal
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    let chat = getChat(chatId);
    switch (chat) {
      case (null) {
        return #Err(#InvalidId);
      };
      case (?chat) {
        if (caller != chat.owner) {
          return #Err(#Unauthorized);
        };
        return #Ok(chat);
      };
    };
  };

  public shared({ caller }) func update_chat_metadata(updateChatObject : Types.UpdateChatObject) : async Types.ChatIdResult {
    // disabled
    return #Err(#Unauthorized);
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    switch (getChat(updateChatObject.id)) {
      case (null) {
        return #Err(#InvalidId);
      };
      case (?chat) {
        // only owner may update
        if (chat.owner != caller) {
          return #Err(#Unauthorized);
        };

        let updatedChat : Types.Chat = {
          id = chat.id;
          messages = chat.messages;
          owner = chat.owner;
          creationTime = chat.creationTime;
          firstMessagePreview = chat.firstMessagePreview;
          chatTitle = updateChatObject.chatTitle;
        };

        let chatUpdated = putChat(updatedChat);
        return #Ok(chatUpdated);
      };
    };
  };

  public shared({ caller }) func update_chat_messages(chatId : Text, updatedMessages : [Types.Message]) : async Types.ChatIdResult {
    // disabled
    return #Err(#Unauthorized);
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    switch (getChat(chatId)) {
      case (null) {
        return #Err(#InvalidId);
      };
      case (?chat) {
        // only owner may update
        if (chat.owner != caller) {
          return #Err(#Unauthorized);
        };

        let updatedChat : Types.Chat = {
          id = chat.id;
          messages = updatedMessages;
          owner = chat.owner;
          creationTime = chat.creationTime;
          firstMessagePreview = chat.firstMessagePreview;
          chatTitle = chat.chatTitle;
        };

        let chatUpdated = putChat(updatedChat);
        return #Ok(chatUpdated);
      };
    };
  };

  public shared ({caller}) func delete_chat(chatId : Text) : async Types.ChatResult {
    // disabled
    return #Err(#Unauthorized);
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    let chat = getChat(chatId);
    switch (chat) {
      case (null) {
        return #Err(#InvalidId);
      };
      case (?chat) {
        if (caller != chat.owner) {
          return #Err(#Unauthorized);
        };
        let userChatDeletionResult = deleteUserChat(caller, chatId);
        let chatDeletionResult = deleteChat(chatId);
        return #Ok(chat);
      };
    };
  };

// User Info and Settings
// User Info
  private func getUserInfo(user : Principal) : ?Types.UserInfo {
    switch (userInfoStorage.get(user)) {
      case (null) { return null; };
      case (?userInfo) { return ?userInfo; };
    };
  };

  private func putUserInfo(user : Principal, userInfo : Types.UserInfo) : Bool {
    userInfoStorage.put(user, userInfo);
    return true;
  };

  public shared query ({caller}) func get_caller_user_info() : async Types.UserInfoResult {
    // don't allow anonymous Principal
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    switch (getUserInfo(caller)) {
      case (null) {
        // No settings stored yet
        return #Err(#InvalidId);
      };
      case (?userInfo) { return #Ok(userInfo); };
    };   
  };

  public shared query ({caller}) func get_user_info_admin(user : Text) : async Types.UserInfoResult {
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};
    if (not Principal.isController(caller)) {
      return #Err(#Unauthorized);
    };

    switch (getUserInfo(Principal.fromText(user))) {
      case (null) {
        // No settings stored yet
        return #Err(#InvalidId);
      };
      case (?userInfo) { return #Ok(userInfo); };
    };   
  };

  public query (msg) func getUsersAdmin() : async Types.GetUsersResult {
    if (Principal.isAnonymous(msg.caller)) {
      return #Err(#Unauthorized);
		};
    if (not Principal.isController(msg.caller)) {
      return #Err(#Unauthorized);
    };

    let users = Iter.toArray(userInfoStorage.keys());
    let userTexts = Array.map<Principal, Text>(
      users,
      func (p: Principal) : Text { Principal.toText(p) }
    );

    return #Ok(userTexts);
  };


  public shared ({ caller }) func update_caller_user_info(updatedInfoObject : Types.UserInfoInput) : async Types.UpdateUserInfoResult {
    // don't allow anonymous Principal
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    switch (updatedInfoObject.emailAddress) {
      case (null) {};
      case (?emailAddress) {
        if (emailAddress.size() > 70) {
          return #Err(#Unauthorized);
        };
      };
    };

    switch (getUserInfo(caller)) {
      case (null) {
        // No settings stored yet, create new entry  
        let newUserInfo : Types.UserInfo = {
          emailAddress : ?Text = updatedInfoObject.emailAddress;
          isPremiumAccount : Bool = false;
          createdAt : Nat64 = Nat64.fromNat(Int.abs(Time.now()));
        };

        let infoCreated = putUserInfo(caller, newUserInfo);
        return #Ok(infoCreated);
      };
      case (?userInfo) {
        let updatedUserInfo : Types.UserInfo = {
          emailAddress : ?Text = updatedInfoObject.emailAddress;
          isPremiumAccount : Bool = userInfo.isPremiumAccount;
          createdAt : Nat64 = userInfo.createdAt;
        };

        let infoUpdated = putUserInfo(caller, updatedUserInfo);
        return #Ok(infoUpdated);
      };
    };
  };

  public shared ({ caller }) func make_caller_account_premium(paymentInfoObject : Types.PaymentInfoInput) : async Types.UpdateUserInfoResult {
    // don't allow anonymous Principal
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    // Only Principals registered as custodians can access this function
    // TODO: replace this with a payment check (via block_index in paymentInfoObject)
    if (List.some(custodians, func (custodian : Principal) : Bool { custodian == caller })) {
      switch (getUserInfo(caller)) {
        case (null) {
          // No settings stored yet
          return #Err(#InvalidId);
        };
        case (?userInfo) {
          let updatedUserInfo : Types.UserInfo = {
            emailAddress : ?Text = userInfo.emailAddress;
            isPremiumAccount : Bool = true;
            createdAt : Nat64 = userInfo.createdAt;
          };

          let infoUpdated = putUserInfo(caller, updatedUserInfo);
          return #Ok(infoUpdated);
        };
      };
    };
    return #Err(#Unauthorized);
  };

// Logins
  stable var userToLoginsStorageStable : [(Principal, List.List<Types.LoginEvent>)] = [];
  var userToLoginsStorage : HashMap.HashMap<Principal, List.List<Types.LoginEvent>> = HashMap.HashMap(0, Principal.equal, Principal.hash);

  // Log a login event for the caller
  public shared (msg) func logLogin() : async Types.UpdateUserInfoResult {
    if (Principal.isAnonymous(msg.caller)) {
      return #Err(#Unauthorized);
		};

    let user = msg.caller;
    let timestamp = Nat64.fromNat(Int.abs(Time.now()));
    let event : Types.LoginEvent = { timestamp = timestamp; principal = Principal.toText(user); };

    // Get the current list of events for this user, or an empty list
    let currentEvents = switch (userToLoginsStorage.get(user)) {
      case null {
        // First login, so create a user entry too
        let userInfo : Types.UserInfo = {
          emailAddress: ?Text = null;
          isPremiumAccount : Bool = false;
          createdAt : Nat64 = timestamp;
        };
        let result = putUserInfo(user, userInfo);
        List.nil<Types.LoginEvent>()
      };
      case (?events) { events };
    };

    // Prepend the new event to the user's list
    let updatedEvents = List.push(event, currentEvents);

    // Update the HashMap
    let _ = userToLoginsStorage.put(user, updatedEvents);
    return #Ok(true);
  };

  // Retrieve all login events for a user
  public query (msg) func getLoginEventsAdmin(user : Text) : async Types.LoginEventsResult {
    if (Principal.isAnonymous(msg.caller)) {
      return #Err(#Unauthorized);
		};
    if (not Principal.isController(msg.caller)) {
      return #Err(#Unauthorized);
    };

    switch (userToLoginsStorage.get(Principal.fromText(user))) {
      case null { #Ok([]) };
      case (?events) { #Ok(List.toArray(events)) };
    }
  };

// Chat Settings

  /**
   * A simple function to retrieve the user's chat settings, this provides no protection so should only be called if
   * the caller has permissions to read the settings data
   *
   * @return The user's settings if they exist, otherwise an empty List
  */
  private func getUserChatSettings(user : Principal) : ?Types.UserChatSettings {
    switch (userChatSettingsStorage.get(user)) {
      case (null) { return null; };
      case (?userChatSettings) { return ?userChatSettings; };
    };
  };

  /**
   * Simple function to store user chat settings in the database. There are no protections so this function should only
   * be called if the caller has permissions to store the user settings to the database
   *
   * @return Confirmation that the user settings were stored successfully
  */
  private func putUserChatSettings(user : Principal, userChatSettings : Types.UserChatSettings) : Bool {
    userChatSettingsStorage.put(user, userChatSettings);
    return true;
  };

  public shared query ({caller}) func get_caller_chat_settings() : async Types.UserChatSettingsResult {
    // don't allow anonymous Principal
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    switch (getUserChatSettings(caller)) {
      case (null) {
        // No settings stored yet, return default
        let userChatSettings : Types.UserChatSettings = {
          temperature = 0.6;
          responseLength = "Long";
          saveChats = true;
          selectedAiModelId = "";
          systemPrompt = "You are a helpful, respectful and honest assistant.";
        };
        return #Ok(userChatSettings);
      };
      case (?userChatSettings) { return #Ok(userChatSettings); };
    };   
  };

  public shared({ caller }) func update_caller_chat_settings(updatedSettingsObject : Types.UserChatSettings) : async Types.UpdateUserChatSettingsResult {
    // disabled
    return #Err(#Unauthorized);
    if (Principal.isAnonymous(caller)) {
      return #Err(#Unauthorized);
		};

    let settingsUpdated = putUserChatSettings(caller, updatedSettingsObject);
    return #Ok(settingsUpdated);
  };

// Max mAIner topups
  stable var maxMainerTopups : List.List<Types.TopUpRecord> = List.nil<Types.TopUpRecord>();

  private func putMaxMainerTopup(topupEntry : Types.TopUpRecord) : Bool {
      maxMainerTopups := List.push<Types.TopUpRecord>(topupEntry, maxMainerTopups);
      return true;
  };

  private func getMaxMainerTopup(paymentTransactionBlockId : Nat64) : ?Types.TopUpRecord {
      return List.find<Types.TopUpRecord>(maxMainerTopups, func(topupEntry: Types.TopUpRecord) : Bool { topupEntry.paymentTransactionBlockId == paymentTransactionBlockId } ); 
  };

  private func getMaxMainerTopups() : [Types.TopUpRecord] {
      return List.toArray<Types.TopUpRecord>(maxMainerTopups);
  };

  private func removeMaxMainerTopup(paymentTransactionBlockId : Nat64) : Bool {
      maxMainerTopups := List.filter(maxMainerTopups, func(topupEntry: Types.TopUpRecord) : Bool { topupEntry.paymentTransactionBlockId != paymentTransactionBlockId });
      return true;
  };

  private func addMaxMainerTopups(entriesToAdd : List.List<Types.TopUpRecord>) : Bool {
      maxMainerTopups := List.append<Types.TopUpRecord>(entriesToAdd, maxMainerTopups);
      return true;
  };

  public shared (msg) func addMaxMainerTopup(maxTopUpInput : Types.MaxMainerTopUpInput) : async Types.MaxMainerTopUpStorageResult {
      if (Principal.isAnonymous(msg.caller)) {
          return #Err(#Unauthorized);
      };

      // ensure caller is user
      switch (getUserInfo(msg.caller)) {
        case (null) {
          // Not a user
          return #Err(#Unauthorized);
        };
        case (?userInfo) {
          let newEntry : Types.TopUpRecord = {
            timestamp : Nat64 = Nat64.fromNat(Int.abs(Time.now()));
            caller : Text = Principal.toText(msg.caller);
            paymentTransactionBlockId : Nat64 = maxTopUpInput.paymentTransactionBlockId;
            toppedUpMainerId : Text = maxTopUpInput.toppedUpMainerId;
            amount : Nat = maxTopUpInput.amount;
          };
          
          let result = putMaxMainerTopup(newEntry);

          return #Ok({stored = true;});          
        };
      };
  };

  public query (msg) func getMaxMainerTopupsAdmin() : async Types.MaxMainerTopUpsResult {
      if (Principal.isAnonymous(msg.caller)) {
          return #Err(#Unauthorized);
      };
      if (not Principal.isController(msg.caller)) {
        return #Err(#Unauthorized);
      };
      
      let result = getMaxMainerTopups();

      return #Ok(result);
  };

  // Max topups archive
  stable var archivedMaxMainerTopups : List.List<Types.TopUpRecord> = List.nil<Types.TopUpRecord>();

  private func getArchivedMaxMainerTopups() : [Types.TopUpRecord] {
      return List.toArray<Types.TopUpRecord>(archivedMaxMainerTopups);
  };

  private func addArchivedMaxMainerTopups(topupsToAdd : List.List<Types.TopUpRecord>) : Bool {
      archivedMaxMainerTopups := List.append<Types.TopUpRecord>(topupsToAdd, archivedMaxMainerTopups);
      return true;
  };

  private func archiveMaxMainerTopups() : Bool {
    switch (addArchivedMaxMainerTopups(maxMainerTopups)) {
      case (false) {
        return false;
      };
      case (true) {
        // then reset max topups
        maxMainerTopups := List.nil<Types.TopUpRecord>();
        return true;
      };
    };
  };

  public shared query (msg) func getArchivedMaxMainerTopupsAdmin() : async Types.MaxMainerTopUpsResult {
    if (Principal.isAnonymous(msg.caller)) {
      return #Err(#Unauthorized);
    };
    if (not Principal.isController(msg.caller)) {
      return #Err(#Unauthorized);
    };

    let archivedTopupsArray : [Types.TopUpRecord] = getArchivedMaxMainerTopups();

    return #Ok(archivedTopupsArray);
  };

  public shared query (msg) func getNumArchivedMaxMainerTopupsAdmin() : async Types.NatResult {
    if (Principal.isAnonymous(msg.caller)) {
      return #Err(#Unauthorized);
    };
    if (not Principal.isController(msg.caller)) {
      return #Err(#Unauthorized);
    };

    let archivedTopupsArray : [Types.TopUpRecord] = getArchivedMaxMainerTopups();

    return #Ok(archivedTopupsArray.size());
  };

  public shared (msg) func archiveMaxMainerTopupsAdmin() : async Types.BoolResult {
    if (Principal.isAnonymous(msg.caller)) {
      return #Err(#Unauthorized);
    };
    if (not Principal.isController(msg.caller)) {
      return #Err(#Unauthorized);
    };
    return #Ok(archiveMaxMainerTopups());
  };

// Email Signups from Website
  stable var emailSubscribersStorageStable : [(Text, Types.EmailSubscriber)] = [];
  var emailSubscribersStorage : HashMap.HashMap<Text, Types.EmailSubscriber> = HashMap.HashMap(0, Text.equal, Text.hash);

  // Add a user as new email subscriber
  private func putEmailSubscriber(emailSubscriber : Types.EmailSubscriber) : Text {
    emailSubscribersStorage.put(emailSubscriber.emailAddress, emailSubscriber);
    return emailSubscriber.emailAddress;
  };

  // Retrieve an email subscriber by email address
  private func getEmailSubscriber(emailAddress : Text) : ?Types.EmailSubscriber {
    let result = emailSubscribersStorage.get(emailAddress);
    return result;
  };

  // User can submit a form to sign up for email updates
    // For now, we only capture the email address provided by the user and on which page they submitted the form
  public shared ({caller}) func submit_signup_form(submittedSignUpForm : Types.SignUpFormInput) : async Text {
    if (submittedSignUpForm.emailAddress.size() > 70) {
      return "There was an error signing up. Please try again.";
    };
    switch(getEmailSubscriber(submittedSignUpForm.emailAddress)) {
      case null {
        // New subscriber
        let emailSubscriber : Types.EmailSubscriber = {
          emailAddress: Text = submittedSignUpForm.emailAddress;
          pageSubmittedFrom: Text = submittedSignUpForm.pageSubmittedFrom;
          subscribedAt: Nat64 = Nat64.fromNat(Int.abs(Time.now()));
        };
        let result = putEmailSubscriber(emailSubscriber);
        if (result != emailSubscriber.emailAddress) {
          return "There was an error signing up. Please try again.";
        };
        return "Successfully signed up!";
      };
      case _ { return "Already signed up!"; };
    };  
  };

  // Function for custodian to get all email subscribers
  public shared query ({ caller }) func get_email_subscribers() : async [(Text, Types.EmailSubscriber)] {
    // don't allow anonymous Principal
    if (Principal.isAnonymous(caller)) {
      return [];
		};

    // Only Controllers can access this function
    if (not Principal.isController(caller)) {
      return [];
    };
    
    return Iter.toArray(emailSubscribersStorage.entries());
  };

  // Function for custodian to delete an email subscriber
  public shared({ caller }) func delete_email_subscriber(emailAddress : Text) : async Bool {
    // don't allow anonymous Principal
    if (Principal.isAnonymous(caller)) {
      return false;
		};

    // Only Principals registered as custodians can access this function
    if (List.some(custodians, func (custodian : Principal) : Bool { custodian == caller })) {
      emailSubscribersStorage.delete(emailAddress);
      return true;
    };
    return false;
  };

// Upgrade Hooks
  system func preupgrade() {
    userChatsStorageStable := Iter.toArray(userChatsStorage.entries());
    userChatSettingsStorageStable := Iter.toArray(userChatSettingsStorage.entries());
    chatsStorageStable := Iter.toArray(chatsStorage.entries());
    emailSubscribersStorageStable := Iter.toArray(emailSubscribersStorage.entries());
    userInfoStorageStable := Iter.toArray(userInfoStorage.entries());
    userToLoginsStorageStable := Iter.toArray(userToLoginsStorage.entries());
  };

  system func postupgrade() {
    userChatsStorage := HashMap.fromIter(Iter.fromArray(userChatsStorageStable), userChatsStorageStable.size(), Principal.equal, Principal.hash);
    userChatsStorageStable := [];
    userChatSettingsStorage := HashMap.fromIter(Iter.fromArray(userChatSettingsStorageStable), userChatSettingsStorageStable.size(), Principal.equal, Principal.hash);
    userChatSettingsStorageStable := [];    
    chatsStorage := HashMap.fromIter(Iter.fromArray(chatsStorageStable), chatsStorageStable.size(), Text.equal, Text.hash);
    chatsStorageStable := [];
    emailSubscribersStorage := HashMap.fromIter(Iter.fromArray(emailSubscribersStorageStable), emailSubscribersStorageStable.size(), Text.equal, Text.hash);
    emailSubscribersStorageStable := [];
    userInfoStorage := HashMap.fromIter(Iter.fromArray(userInfoStorageStable), userInfoStorageStable.size(), Principal.equal, Principal.hash);
    userInfoStorageStable := [];
    userToLoginsStorage := HashMap.fromIter(Iter.fromArray(userToLoginsStorageStable), userToLoginsStorageStable.size(), Principal.equal, Principal.hash);
    userToLoginsStorageStable := [];
  };
};
