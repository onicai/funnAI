THIS DOCUMENT IS NO LONGER USED

Use `README-prd-upgrade-commands.md` instead


TODO: ensure there is no useful info here and then delete it.





OLD-OLD-OLD

# funnAI - Upgrade Procedure for PoAIW Canisters in prd network

This document outlines the procedure to upgrade the PoAIW canisters of the funnAI application on the prd network, where the production release is running.

This procedure must be followed strictly to avoid inadvertently breaking the application or losing critical data.

This same procedure can be applied to the other networks, like testing, demo, development, etc.

# Setup a development environment
First step is to follow the instructions of the README.md to set up a development environment.

# Controller Access
You must be a controller to be able to call the Admin endpoints of the canisters.

Run these scripts to verify Admin access:

```bash
# Use conda environment
conda activate llama_cpp_canister

# Ensure the scripts python requirements are installed
pip install -r scripts/requirements.txt

# Set NETWORK environment variable
NETWORK=prd 

# Update the file 'scripts/canister_ids_mainers-<network>.env'
scripts/get_mainers.sh --network $NETWORK

# Verify ownership
scripts/am_i_controller.sh --network $NETWORK --canister-types [all|protocol|mainers]

# If needed, ask another controller to add you
# -> first edit 'scripts/add_controllers.py'
scripts/add_controllers.sh --network $NETWORK --canister-types [all|protocol|mainers]
```

Ensure that you are a controller of the protocol canisters:

- Gamestate (Gs)
- mAInerCreator (Mc)
- Challenger Controller & LLMs (Chctrl & Chllm)
- Judge Controller & LLMs  (Juctrl & Jullm)
- ShareService Controller & LLMs  (Ssctrl & Ssllm)

Most mAIner upgrades go over the Gs > Mc canisters, but if you need direct access to mAIners, make sure you are controller of the mainers as well:
- ALL ShareAgent Controllers (Sactrl)
- ALL PowerAgent Controllers + LLMs (Pwctrl & Pwllm)    (FUTURE)

# Pause funnAI

```bash
# check if it is already paused
dfx canister --network $NETWORK call game_state_canister getPauseProtocolFlag

# then toggle it
dfx canister --network $NETWORK call game_state_canister togglePauseProtocolFlagAdmin
```

# Verify in logs that all is paused

Run these scripts:

```bash
# Update the file 'scripts/canister_ids_mainers-<network>.env'
scripts/get_mainers.sh --network $NETWORK

# Then run these in 3 separate windows
scripts/monitor_logs.sh --network $NETWORK --canister-types [all|protocol|mainers]
scripts/monitor_gamestate_metrics.sh --network $NETWORK 
```

Then view the logs to ensure that:

- GameState is not giving any work to the Challenger, Judge & mAIners
  ```bash
  [...] Challenger: generateChallenge - challengeTopicResult error : #Other("Protocol is currently paused")
  
  [...] Judge:  scoreNextSubmission - submissionResult error : #Other("Protocol is currently paused")

  [...] mAIner (#ShareAgent): pullNextChallenge - challengeResult error : #Other("Protocol is currently paused")

  ```
- Challenger is not working on a Challenge generation
- ShareService is not working on a response generation
- ShareService Queue is empty
- PowerMainers are not working on a response generation (FUTURE)
- PowerMainers Queue is empty (FUTURE)
- Judge is not working on a score generation

# Upgrade of GameState

see README-prd-upgrade-commands.md

# Reinstall of GameState

This is not something we should do, because all data is lost, but this is the procedure:

```bash
NETWORK=prd

# from funnAI folder
scripts/scripts-gamestate/deploy.sh --network $NETWORK --mode reinstall

# Reconnect Challenger, Judge & mAInerCreator, simply by doing an upgrade
# from folder: PoAIW
scripts/deploy-challenger.sh --network $NETWORK --mode upgrade
scripts/deploy-judge.sh --network $NETWORK --mode upgrade
scripts/deploy-mainer-creator.sh --network $NETWORK --mode upgrade
# From folder funnAI:
scripts/scripts-gamestate/register-all.sh --network $NETWORK

# Reconnect ShareService, by doing an upgrade
# from folder: funnAI
dfx canister call game_state_canister addMainerAgentCanisterAdmin '(record { 
    address = "rilmv-caaaa-aaaaa-qandq-cai" ; 
    subnet = "snjp4-xlbw4-mnbog-ddwy6-6ckfd-2w5a2-eipqo-7l436-pxqkh-l6fuv-vae"; 
    canisterType = variant { MainerAgent = variant { ShareService } }; 
    creationTimestamp = 1750799357;
    createdBy = principal "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae";
    ownedBy = principal "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae";
    status = variant { Running };
    mainerConfig = record {
            mainerAgentCanisterType = variant { ShareService };
            selectedLLM = opt variant {Qwen2_5_500M};
            cyclesForMainer = 0;
            subnetCtrl = "snjp4-xlbw4-mnbog-ddwy6-6ckfd-2w5a2-eipqo-7l436-pxqkh-l6fuv-vae";
            subnetLlm = "4zbus-z2bmt-ilreg-xakz4-6tyre-hsqj4-slb4g-zjwqo-snjcc-iqphi-3qe";
        };
    })' --network $NETWORK
dfx canister call game_state_canister addOfficialCanister '(record {
    address = "rilmv-caaaa-aaaaa-qandq-cai" ; 
    subnet = "snjp4-xlbw4-mnbog-ddwy6-6ckfd-2w5a2-eipqo-7l436-pxqkh-l6fuv-vae"; 
    canisterType = variant { MainerAgent = variant { ShareService } } 
    })' --network $NETWORK
dfx canister call game_state_canister getOfficialCanistersAdmin --network $NETWORK
scripts/scripts-gamestate/deploy-mainers-ShareService-Controller-via-gamestate.sh --mode upgrade --network $NETWORK

# Update the wasm-hash, using the Admin owned test mAIner ShareAgent
dfx canister call game_state_canister deriveNewMainerAgentCanisterWasmHashAdmin '(record {address="vg3fp-pyaaa-aaaaa-qavba-cai"; textNote="Reinstall of GameState"})' --network $NETWORK

# Set the parameters according to README-prd-settings.md
```


# Upgrade of Challenger & Judge Controllers & ShareService Controllers

see README-prd-upgrade-commands.md

# Reinstall of Challenger & Judge Controllers

see README-prd-upgrade-commands.md


# Upgrade of user mAIner Controllers (ShareAgent, Own)

Upgrading mAIner Controllers involves several steps, because the mAIners are upgraded via the mAInerCreator.

- Build the wasm & did file for the new mAIner code & do local upgrade test
  
  This will surface any forward compatibility issues that you must uncover before continuing.

    ```bash
        # Start the local network in a separate terminal
        # From folder: funnAI
        dfx start --clean

        # From folder: PoAIW/src/mAIner
        git checkout <currently deployed version to prd network>
        dfx deploy mainer_ctrlb_canister_0 --mode install
        
        git checkout <new version to deploy to prd network>
        dfx deploy mainer_ctrlb_canister_0 --mode upgrade

        # In case the upgrade fails due to forward compatibility issues, but you have to make the change
        # Use reinstall
        # NOTE: The mAIner Agents deploys to prd also must use `reinstall` & this will result in all their stable data being lost !
        #       This is not disastrous, it is mainly that the following stable data will be lost:
        #       - user settings like CycleBurnRate
        #       - generatedResponses and submittedResponses
        dfx deploy mainer_ctrlb_canister_0 --mode reinstall
    ```

- Copy & rename these files to the mAInerCreator/files folder:

    - `PoAIW/src/mAIner/.dfx/local/canisters/mainer_ctrlb_canister_0/mainer_ctrlb_canister_0.did` to `PoAIW/src/mAInerCreator/files/mainer_ctrlb_canister.did`
    - `PoAIW/src/mAIner/.dfx/local/canisters/mainer_ctrlb_canister_0/mainer_ctrlb_canister_0.wasm` to `PoAIW/src/mAInerCreator/files/mainer_ctrlb_canister.wasm`
    
- Upgrade the mAInerCreator. 

    This command will:
    - Deploy the latest mAInerCreator code
    - Upload `files/mainer_ctrlb_canister.wasm`
    - Upload `files/llama_cpp_canister.wasm`  *(For LLM upgrades described below)*

    ```bash
        # from folder: PoAIW
        NETWORK=prd
        scripts/deploy-mainer-creator.sh --network $NETWORK --mode upgrade

        # If you made any changes to the mAInerCreator canister id, re-register it with the GameState
        # From folder funnAI:
        scripts/scripts-gamestate/register-all.sh --network $NETWORK
    ```

- Upgrade all the ShareAgent mAIners

    ```bash
        # from folder: funnAI
        NETWORK=prd

        # First try it out on one of our mAIners
        scripts/scripts-gamestate/deploy-mainers-ShareAgent-via-gamestate.sh --mode upgrade --canister <canisterId> --network $NETWORK
        # NOTE: `--mode reinstall [--force]` is also supported.

        # Update the file 'scripts/canister_ids_mainers-<network>.env'
        scripts/get_mainers.sh --network $NETWORK

        # Upgrade ALL mAIners
        scripts/upgrade_mainers.sh --network $NETWORK

        # NOTE: To reinstall ALL mAIners
        scripts/reinstall_mainers.sh --network $NETWORK
    ```

- Update gamestate to the latest wasmhash. <canisterId> is the address of one of the upgraded ShareAgent canisters

    ```bash
        # from folder: funnAI
        NETWORK=prd
        dfx canister call game_state_canister deriveNewMainerAgentCanisterWasmHashAdmin '(record {address="<canisterId>"; textNote="New wasm deployed"})' --network $NETWORK
    ```


# Update Challenger, ShareService & Judge LLMs

see README-prd-upgrade-commands.md