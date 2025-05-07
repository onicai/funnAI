# May 5, 2025

The following canisters were deployed to "testing" network as part of the demo deployment:

-> Copy/Paste this into your terminal...
```bash
GAMESTATE="cc2po-yiaaa-aaaaj-az75q-cai"
MAINER_CREATOR="cx56d-zaaaa-aaaaj-az76a-cai"
CHALLENGER="c66v7-piaaa-aaaaj-az77q-cai"
CHALLENGER_LLM_0="cq4yx-uyaaa-aaaaj-az76q-cai"
CHALLENGER_LLM_1="cz7tl-cqaaa-aaaaj-az77a-cai"
JUDGE="uln7r-5yaaa-aaaaj-a2aba-cai"
JUDGE_LLM_0="ufpsz-giaaa-aaaaj-a2aaa-cai"
JUDGE_LLM_1="ucoun-lqaaa-aaaaj-a2aaq-cai"
SHARE_SERVICE="uqidu-haaaa-aaaaj-a2adq-cai"
SHARE_SERVICE_LLM_0="v5gh2-iiaaa-aaaaj-a2aea-cai"
SHARE_SERVICE_LLM_1="v2hbo-fqaaa-aaaaj-a2aeq-cai"
MAINER_SHARE_AGENT_1="vteks-tyaaa-aaaaj-a2afa-cai" 
MAINER_SHARE_AGENT_2=""
MAINER_OWN_0="vgd37-sqaaa-aaaaj-a2agq-cai"
MAINER_OWN_0_LLM_0="vpaqd-eyaaa-aaaaj-a2aha-cai"
MAINER_OWN_1="vibwx-jaaaa-aaaaj-a2ahq-cai"
MAINER_OWN_1_LLM_0=""
```

========================================================================
To add another LLM to the ShareService Controller uqidu-haaaa-aaaaj-a2adq-cai:
 
(-) First add 5 TCycles to the GameState canister:
dfx wallet send  cc2po-yiaaa-aaaaj-az75q-cai 5000000000000 --network testing 
(-) Then add the LLM to the ShareService Controller by calling the GameState:
dfx canister call cc2po-yiaaa-aaaaj-az75q-cai addLlmCanisterToMainer  'record {
      status = variant { ControllerCreated };
      canisterType = variant { MainerAgent = variant { ShareService } };
      ownedBy = principal "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae";
      creationTimestamp = 1_746_639_960_946_013_657 : nat64;
      createdBy = principal "cc2po-yiaaa-aaaaj-az75q-cai";
      mainerConfig = record {
        selectedLLM = opt variant { Qwen2_5_500M };
        mainerAgentCanisterType = variant { ShareService };
      };
      address = "uqidu-haaaa-aaaaj-a2adq-cai";
    }' --network testing
 
The timers are running! 
To stop timers for ShareService: 
dfx canister call uqidu-haaaa-aaaaj-a2adq-cai stopTimerExecutionAdmin --network testing

To stop timers for the ShareAgents: 
dfx canister call vteks-tyaaa-aaaaj-a2afa-cai stopTimerExecutionAdmin --network testing

To stop timers for the Owns:
dfx canister call vgd37-sqaaa-aaaaj-a2agq-cai stopTimerExecutionAdmin --network testing

## Debugging

### Logs

You can retrieve the log of a canister as follows:

```bash
# Continuous monitoring:
# To monitor the logs, run this script from the FunnAI folder
# -> It will write to the screen & also write individual files in scripts/logs/
# -> You must be a controller or log-viewer
#    % dfx canister update-settings <canister-name> --add-log-viewer <principal-id>
scripts/logs.sh --network testing

# From anywhere
dfx canister logs <canister-id> --network testing

# from folder: PoAIW/src/mAInerCreator
dfx canister logs mainer_creator_canister --network testing
```

### Top-up a Canister

```bash
# Top up cycles by sending 1Tcycles
dfx wallet --network testing send <canister-id> 1000000000000
```

### Start & Stop timers

```bash
dfx canister --network testing call $CHALLENGER stopTimerExecutionAdmin
dfx canister --network testing call $JUDGE stopTimerExecutionAdmin
dfx canister --network testing call $MAINER_OWN stopTimerExecutionAdmin
dfx canister --network testing call $MAINER_SERVICE stopTimerExecutionAdmin
dfx canister --network testing call $MAINER_AGENT1 stopTimerExecutionAdmin
dfx canister --network testing call $MAINER_AGENT2 stopTimerExecutionAdmin

dfx canister --network testing call $CHALLENGER startTimerExecutionAdmin
dfx canister --network testing call $JUDGE startTimerExecutionAdmin
dfx canister --network testing call $MAINER_OWN startTimerExecutionAdmin
dfx canister --network testing call $MAINER_SERVICE startTimerExecutionAdmin
dfx canister --network testing call $MAINER_AGENT1 startTimerExecutionAdmin
dfx canister --network testing call $MAINER_AGENT2 startTimerExecutionAdmin
```

### Step by Step testing

Run these tests while the timers are all off

```bash
# Verify Challenger challenge generations
dfx canister --network testing call $GAMESTATE getCurrentChallengesAdmin --output json
dfx canister --network testing call $GAMESTATE getNumCurrentChallengesAdmin --output json

# Verify mAIner response generations
# Note: submissionStatus changes from #Submitted > #Judging > #Judged
dfx canister --network testing call $GAMESTATE  getSubmissionsAdmin --output json
dfx canister --network testing call $GAMESTATE  getNumSubmissionsAdmin --output json

dfx canister --network testing call $GAMESTATE getOpenSubmissionsAdmin --output json
dfx canister --network testing call $GAMESTATE getNumOpenSubmissionsAdmin --output json

# Verify Judge score generations
dfx canister --network testing call $GAMESTATE getScoredChallengesAdmin --output json
dfx canister --network testing call $GAMESTATE getNumScoredChallengesAdmin --output json

# Generate a single Challenge
dfx canister --network testing call $CHALLENGER generateNewChallenge

# Trigger a single Response of a mAIner
# Use one of these: $MAINER_OWN, $MAINER_AGENT1, $MAINER_AGENT2
dfx canister --network testing call $MAINER_OWN getMainerCanisterType
dfx canister --network testing call $MAINER_OWN triggerChallengeResponseAdmin
dfx canister --network testing call $MAINER_OWN getChallengeQueueAdmin --output json
# -> Wait, and then call
dfx canister --network testing call $MAINER_OWN  getSubmittedResponsesAdmin --output json
dfx canister --network testing call $GAMESTATE  getSubmissionsAdmin --output json
dfx canister --network testing call $GAMESTATE  getNumSubmissionsAdmin --output json
# -> For the #ShareAgents, when the #ShareService timer is off, you need to do more
# -> The #ShareService Queue will contain items, which you can trigger to be done
dfx canister --network testing call $MAINER_SERVICE getMainerCanisterType
dfx canister --network testing call $MAINER_SERVICE getChallengeQueueAdmin --output json
dfx canister --network testing call $MAINER_SERVICE triggerChallengeResponseAdmin

# Trigger a single score generation manually
dfx canister --network testing call $JUDGE triggerScoreSubmissionAdmin
# -> Wait, and then call
dfx canister --network testing call $GAMESTATE getScoredChallengesAdmin --output json
dfx canister --network testing call $GAMESTATE getNumScoredChallengesAdmin --output json

```

### Get canister-ids of the registered LLMs

```bash
# Use $MAINER_OWN or $MAINER_SERVICE
# Calling it in sequence will cycle through the registered LLMs
# Note that any registered LLM is successfully created, even if there was a timeout 
dfx canister --network testing call $MAINER_OWN getRoundRobinCanister
```

### Add another LLM to a mAIner Agent

```bash
# Use $MAINER_OWN or $MAINER_SERVICE
dfx canister --network testing call $MAINER_CREATOR testCreateMainerLlmCanister "(\"$MAINER_OWN\")"
```

### LLM canisters

If an LLM is not behaving, use commands from the README of the llama_cpp_canister repo
to debug it. These are some useful ones:

```bash
# Use $MAINER_OWN_LLM or $MAINER_SERVICE_LLM

# Get status
dfx canister --network testing status $MAINER_OWN_LLM

# Top up cycles by sending 1Tcycles
dfx wallet --network testing send $MAINER_OWN_LLM 1000000000000

# Get current balance of cycles (Fails if cycles are below frozen canister limit !)
dfx canister --network testing status $MAINER_OWN_LLM 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}'

# Check health
dfx canister --network testing call $MAINER_OWN_LLM health
dfx canister --network testing call $MAINER_OWN_LLM ready

# If this returns 13, it means that the LLM upload & model load worked
# This call is done after that by the mAInerCreator canister
dfx canister --network testing call $MAINER_OWN_LLM get_max_tokens

# Chat with it directly
# 0. Check everything is ok
dfx canister --network testing call $MAINER_OWN_LLM ready

# 1. Create a new chat
dfx canister --network testing call $MAINER_OWN_LLM new_chat '(record { 
    args = vec {
    "--prompt-cache"; "prompt.cache"; 
    "--cache-type-k"; "q8_0";
    } 
})'
# 2. Repeat this call until `prompt_remaining` in the response is empty. 
# This ingest the prompt into the prompt-cache, using multiple update calls: 
# (-) Keep sending the full prompt
# (-) Use `"-n"; "1"`, so it does not generate new tokens
dfx canister --network testing call $MAINER_OWN_LLM run_update '(record { 
    args = vec {
    "--prompt-cache"; "prompt.cache"; "--prompt-cache-all"; 
    "--cache-type-k"; "q8_0";
    "--repeat-penalty"; "1.1";
    "--temp"; "0.6";
    "-sp"; 
    "-p"; "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\ngive me a short introduction to LLMs.<|im_end|>\n<|im_start|>assistant\n"; 
    "-n"; "1" 
    } 
})' 

# 3. Generate new tokens:
# Once `prompt_remaining` in the response is empty.
# (-) repeat this call, until `generated_eog=true`
# (-) Use an empty prompt: `"-p"; "";`
# (-) Use `"-n"; "512"`, so it will now generate new tokens 
dfx canister --network testing call $MAINER_OWN_LLM run_update '(record { 
    args = vec {
    "--prompt-cache"; "prompt.cache"; "--prompt-cache-all"; 
    "--cache-type-k"; "q8_0";
    "--repeat-penalty"; "1.1";
    "--temp"; "0.6";
    "-sp"; 
    "-p"; ""; 
    "-n"; "512" 
    } 
})' 

# Load the model (DO NOT DO THIS THOUGH, IT IS ALREADY LOADED)
dfx canister --network testing call $MAINER_OWN_LLM load_model '(record { 
    args = vec {
      "--model"; "models/model.gguf";
      "--cache-type-k"; "q8_0";
    }
  })'
```