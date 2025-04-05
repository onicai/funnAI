# April 2, 2025

The following canisters were deployed to main-net as part of the demo deployment:

Fixed:
- GameState canister    : "xzpy6-hiaaa-aaaaj-az4pq-cai"
- mAInerCreator canister: "movk5-tyaaa-aaaaj-az64q-cai"

- Challenger:
  - ctrlb canister      : "lxb3x-jyaaa-aaaaj-azzta-cai"
  - llm_0               : "lmehs-taaaa-aaaaj-azzrq-cai"
  - llm_1               : "l6cql-7qaaa-aaaaj-azzsq-cai"

- Judge:
  - ctrlb canister      : "xxnvw-4yaaa-aaaaj-az4oq-cai"
  - llm_0               : "xljph-lyaaa-aaaaj-az4mq-cai"
  - llm_1               : "xcke3-5qaaa-aaaaj-az4na-cai"

Variable - installed via mAInerCreator
- mAIner Agent type #Own:
  - ctrlb canister      : "hmhcs-7qaaa-aaaaj-az7ba-cai"
  - llm canister        : 

- mAIner Agent type #ShareService:
  - ctrlb canister      : "h6bvl-taaaa-aaaaj-az7ca-cai"
  - llm canister        : 

- mAIner Agent type #ShareAgent:
  - ctrlb canister      : "hqdyd-iqaaa-aaaaj-az7da-cai"
  - ctrlb canister      : "hxc6x-fiaaa-aaaaj-az7dq-cai"

```bash
# Handy settings...
# These are fixed
GAMESTATE="xzpy6-hiaaa-aaaaj-az4pq-cai"
MAINER_CREATOR="movk5-tyaaa-aaaaj-az64q-cai"

CHALLENGER="lxb3x-jyaaa-aaaaj-azzta-cai"
CHALLENGER_LLM_0="lmehs-taaaa-aaaaj-azzrq-cai"
CHALLENGER_LLM_1="l6cql-7qaaa-aaaaj-azzsq-cai"

JUDGE="xxnvw-4yaaa-aaaaj-az4oq-cai"
JUDGE_LLM_0="xljph-lyaaa-aaaaj-az4mq-cai"
JUDGE_LLM_1="xcke3-5qaaa-aaaaj-az4na-cai"

# These vary
MAINER_OWN="hmhcs-7qaaa-aaaaj-az7ba-cai"
MAINER_OWN_LLM="hlgeg-siaaa-aaaaj-az7bq-cai"
MAINER_SERVICE="h6bvl-taaaa-aaaaj-az7ca-cai"
MAINER_SERVICE_LLM="hzat7-6yaaa-aaaaj-az7cq-cai"
MAINER_AGENT1="hqdyd-iqaaa-aaaaj-az7da-cai" 
MAINER_AGENT2="hxc6x-fiaaa-aaaaj-az7dq-cai"
```

## Debugging

### Logs

You can retrieve the log of a canister as follows:

```bash
# From anywhere
dfx canister logs <canister-id> --ic

# from folder: PoAIW/src/mAInerCreator
dfx canister logs mainer_creator_canister --ic
```

### Start & Stop timers

```bash
dfx canister --ic call $CHALLENGER stopTimerExecutionAdmin
dfx canister --ic call $JUDGE stopTimerExecutionAdmin
dfx canister --ic call $MAINER_OWN stopTimerExecutionAdmin
dfx canister --ic call $MAINER_SERVICE stopTimerExecutionAdmin
dfx canister --ic call $MAINER_AGENT1 stopTimerExecutionAdmin
dfx canister --ic call $MAINER_AGENT2 stopTimerExecutionAdmin

dfx canister --ic call $CHALLENGER startTimerExecutionAdmin
dfx canister --ic call $JUDGE startTimerExecutionAdmin
dfx canister --ic call $MAINER_OWN startTimerExecutionAdmin
dfx canister --ic call $MAINER_SERVICE startTimerExecutionAdmin
dfx canister --ic call $MAINER_AGENT1 startTimerExecutionAdmin
dfx canister --ic call $MAINER_AGENT2 startTimerExecutionAdmin
```

### Step by Step testing

Run these tests while the timers are all off

```bash
# Verify Challenger challenge generations
dfx canister --ic call $GAMESTATE getCurrentChallengesAdmin --output json
dfx canister --ic call $GAMESTATE getNumCurrentChallengesAdmin --output json

# Verify mAIner response generations
# Note: submissionStatus changes from #Submitted > #Judging > #Judged
dfx canister --ic call $GAMESTATE  getSubmissionsAdmin --output json
dfx canister --ic call $GAMESTATE  getNumSubmissionsAdmin --output json

dfx canister --ic call $GAMESTATE getOpenSubmissionsAdmin --output json
dfx canister --ic call $GAMESTATE getNumOpenSubmissionsAdmin --output json

# Verify Judge score generations
dfx canister --ic call $GAMESTATE getScoredChallengesAdmin --output json
dfx canister --ic call $GAMESTATE getNumScoredChallengesAdmin --output json

# Generate a single Challenge
dfx canister --ic call $CHALLENGER generateNewChallenge

# Trigger a single Response of a mAIner
# Use one of these: $MAINER_OWN, $MAINER_AGENT1, $MAINER_AGENT2
dfx canister --ic call $MAINER_OWN getMainerCanisterType
dfx canister --ic call $MAINER_OWN triggerChallengeResponseAdmin
dfx canister --ic call $MAINER_OWN getChallengeQueueAdmin --output json
# -> Wait, and then call
dfx canister --ic call $MAINER_OWN  getSubmittedResponsesAdmin --output json
dfx canister --ic call $GAMESTATE  getSubmissionsAdmin --output json
dfx canister --ic call $GAMESTATE  getNumSubmissionsAdmin --output json
# -> For the #ShareAgents, when the #ShareService timer is off, you need to do more
# -> The #ShareService Queue will contain items, which you can trigger to be done
dfx canister --ic call $MAINER_SERVICE getMainerCanisterType
dfx canister --ic call $MAINER_SERVICE getChallengeQueueAdmin --output json
dfx canister --ic call $MAINER_SERVICE triggerChallengeResponseAdmin

# Trigger a single score generation manually
dfx canister --ic call $JUDGE triggerScoreSubmissionAdmin
# -> Wait, and then call
dfx canister --ic call $GAMESTATE getScoredChallengesAdmin --output json
dfx canister --ic call $GAMESTATE getNumScoredChallengesAdmin --output json

```

### Get canister-ids of the registered LLMs

```bash
# Use $MAINER_OWN or $MAINER_SERVICE
# Calling it in sequence will cycle through the registered LLMs
# Note that any registered LLM is successfully created, even if there was a timeout 
dfx canister --ic call $MAINER_OWN getRoundRobinCanister
```

### Add another LLM to a mAIner Agent

```bash
# Use $MAINER_OWN or $MAINER_SERVICE
dfx canister --ic call $MAINER_CREATOR testCreateMainerLlmCanister "(\"$MAINER_OWN\")"
```

### LLM canisters

If an LLM is not behaving, use commands from the README of the llama_cpp_canister repo
to debug it. These are some useful ones:

```bash
# Use $MAINER_OWN_LLM or $MAINER_SERVICE_LLM

# Get status
dfx canister --ic status $MAINER_OWN_LLM

# Top up cycles by sending 1Tcycles
dfx wallet --ic send $MAINER_OWN_LLM 1000000000000

# Get current balance of cycles (Fails if cycles are below frozen canister limit !)
dfx canister --ic status $MAINER_OWN_LLM 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}'

# Check health
dfx canister --ic call $MAINER_OWN_LLM health
dfx canister --ic call $MAINER_OWN_LLM ready

# If this returns 13, it means that the LLM upload & model load worked
# This call is done after that by the mAInerCreator canister
dfx canister --ic call $MAINER_OWN_LLM get_max_tokens

# Chat with it directly
# 0. Check everything is ok
dfx canister --ic call $MAINER_OWN_LLM ready

# 1. Create a new chat
dfx canister --ic call $MAINER_OWN_LLM new_chat '(record { 
    args = vec {
    "--prompt-cache"; "prompt.cache"; 
    "--cache-type-k"; "q8_0";
    } 
})'
# 2. Repeat this call until `prompt_remaining` in the response is empty. 
# This ingest the prompt into the prompt-cache, using multiple update calls: 
# (-) Keep sending the full prompt
# (-) Use `"-n"; "1"`, so it does not generate new tokens
dfx canister --ic call $MAINER_OWN_LLM run_update '(record { 
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
dfx canister --ic call $MAINER_OWN_LLM run_update '(record { 
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
dfx canister --ic call $MAINER_OWN_LLM load_model '(record { 
    args = vec {
      "--model"; "models/model.gguf";
      "--cache-type-k"; "q8_0";
    }
  })'
```