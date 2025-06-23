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
scripts/am_i_controller.sh –network $NETWORK --canister-types [all|protocol|mainers]

# If needed, ask another controller to add you
# -> first edit 'scripts/add_controllers.py'
scripts/add_controllers.sh –network $NETWORK --canister-types [all|protocol|mainers]
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
scripts/monitor_gamestate_logs.sh --network $NETWORK 
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

Upgrading the GameState is typically easy. Just make sure everything is paused, then run:

```bash
# from funnAI folder
scripts/scripts-gamestate/deploy.sh --network $NETWORK --mode upgrade
```

# Upgrade of Challenger & Judge Controllers & LLM code

```bash

# To upgrade code for both Controllers & LLMs
# from folder: PoAIW
scripts/deploy-challenger.sh --network $NETWORK --mode upgrade
scripts/deploy-judge.sh --network $NETWORK --mode upgrade
# -> If the upgrade fails due to forward compatibility issues, see Reinstall section

# If you made any changes to the controller canister ids, re-register them with the GameState
# From folder funnAI:
scripts/scripts-gamestate/register-all.sh --network $NETWORK
```

# Reinstall of Challenger & Judge Controllers

```bash
# To reinstall the code for the controllers, in case upgrade fails
# from folder: PoAIW/src/Challenger
scripts/deploy.sh --network $NETWORK --mode reinstall
# from folder: PoAIW/src/Judge
scripts/deploy.sh --network $NETWORK --mode reinstall

# -> Now repeat the upgrade steps of previous section.
#    That will tie all the canisters together again.
```

# Upgrade of mAIner Controllers (ShareAgent, Own, ShareService)

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

- Upgrade the ShareService, which is using the regular mAIner code

  Note: allways first upgrade the ShareService, so it has the latest code before you upgrade the mAIners.
        the mAIners register themselves with the ShareService

    ```bash
        from folder: funnAI
        NETWORK=prd
        scripts/scripts-gamestate/deploy-mainers-ShareService-Controller-via-gamestate.sh --mode upgrade --network $NETWORK
        # NOTE: `--mode reinstall` is also supported

        # Note: UNLIKELY you need this, but here how to fix it if the script fails because you also updated GameState and wiped out some data
        # Verify if the ShareService mAIner is still registered with GameState as an official canister
        dfx canister call game_state_canister getOfficialCanistersAdmin --network $NETWORK
        # If not, re-register it with GameState
        dfx canister call game_state_canister addOfficialCanister '(record { address = ; subnet = "<canister-id-of-shareservice>"; canisterType = variant { MainerAgent = variant { ShareService } } })' --network $NETWORK
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

# Upgrade of ShareService Controller

The ShareService Controller is using the regular mAIner code, and you should always update it with the User mAIners.

It is unfortunate, but because the upgrade goes over the mAInerCreator, any code change for the ShareService specifically will modify the mAIner's wasm and the wasmhash, ALL the mAIners must be updated if there is a code change.

# Update Challenger & Judge LLM configuration

This is a more tricky item, but not that hard either, just be CAREFUL !

- You can delete an LLM if you no longer need it or want to move to another subnet, using dfx
- If you delete an LLM or change the configuration, you need to update `PoAIW/llms/Challenger/canister_ids.json` & `PoAIW/llms/Judge/canister_ids.json`
- To deploy a new LLM:
    - If you add a new LLM, ensure it is listed in `PoAIW/llms/Challenger/dfx.json` & `PoAIW/llms/Judge/dfx.json`
        ```json
        {
        "version": 1,
        "canisters": {
            "llm_0": {
                "type": "custom",
                "candid": "../../../../llama_cpp_canister/build/llama_cpp.did",
                "wasm": "../../../../llama_cpp_canister/build/llama_cpp.wasm"
            },
            "llm_1": {
                "type": "custom",
                "candid": "../../../../llama_cpp_canister/build/llama_cpp.did",
                "wasm": "../../../../llama_cpp_canister/build/llama_cpp.wasm"
            },
            ...etc... # NOTE IT IS OK TO HAVE UNUSED LLMs listed here...
        },

        ```
   
    - Update the `2-deploy.sh` script to reflect the changed LLM configuration
        ```bash
        # For Challenger: `PoAIW/llms/Challenger/scripts/2-deploy.sh`
        # Update this section, and also update the Google Drive spreadsheet !
        elif [ "$NETWORK_TYPE" = "prd" ]; then
            NUM_LLMS_DEPLOYED=2
            # Deploy 2 LLMs across two subnets, for failover and redundancy
            # https://docs.google.com/spreadsheets/d/1KeyylEYVs3cQvYXOc9RS0q5eWd_vWIW1UVycfDEIkBk/edit?gid=0#gid=0
            # SUBNET_1_1
            SUBNET_LLM_0="w4asl-4nmyj-qnr7c-6cqq4-tkwmt-o26di-iupkq-vx4kt-asbrx-jzuxh-4ae"
            ...etc...

        # For Judge: `PoAIW/llms/Judge/scripts/2-deploy.sh`
        elif [ "$NETWORK_TYPE" = "prd" ]; then
            NUM_LLMS_DEPLOYED=13
            # Deploy 2 LLMs to subnet where Challenger LLM is running & then 3 LLMs per other subnets
            # https://docs.google.com/spreadsheets/d/1KeyylEYVs3cQvYXOc9RS0q5eWd_vWIW1UVycfDEIkBk/edit?gid=0#gid=0
            # SUBNET_1_1
            SUBNET_LLM_0="w4asl-4nmyj-qnr7c-6cqq4-tkwmt-o26di-iupkq-vx4kt-asbrx-jzuxh-4ae"
            ...etc...
        ```

    - In case you're adding a NEW LLM, you must first manually deploy the canister:

        - Temporarily update the script: `PoAIW/llms/Challenger/scripts/2-deploy.sh` or `PoAIW/llms/Judge/scripts/2-deploy.sh`
            ```bash
            # Temporarily overwrite `llm_id_star` & `llm_id_end`
            llm_id_start=0                           # TEMPORARILY CHANGE - eg. to: 1
            llm_id_end=$((NUM_LLMS_DEPLOYED - 1))    # TEMPORARILY CHANGE - eg. to: 1

            for i in $(seq $llm_id_start $llm_id_end)
            ```
        - Run the deployment for a new LLM
            ```bash
            # from folder: PoAIW/llms/Challenger
            NETWORK=prd
            ./scripts/2-deploy.sh --network $NETWORK --mode install
            ```
        - Verify on ICP Dashboard that the LLM ended up on the correct subnet
        - Update the file: `funnAI/scripts/canister_ids-prd.env`
        - Add the proper controllers. Easiest to just run:
            ```bash
            # from folder: funnAI
            NETWORK=prd
            scripts/add_controllers.sh --network $NETWORK --canister-types protocol
            ```
        - IMPORTANT: RESTORE the script: `PoAIW/llms/Challenger/scripts/2-deploy.sh` or `PoAIW/llms/Judge/scripts/2-deploy.sh`
            ```bash
            llm_id_start=0
            llm_id_end=$((NUM_LLMS_DEPLOYED - 1))

            for i in $(seq $llm_id_start $llm_id_end)
            ```

    - If you changed the NUM_LLMS_DEPLOYED, you must change it also in the following scripts:

        ----------------------------------------------------
        Scripts for the Challenger or Judge LLMs:

        ```bash
        if [ "$NETWORK_TYPE" = "prd" ]; then
            NUM_LLMS_DEPLOYED=...
        fi
        ```

        - `PoAIW/llms/Challenger/scripts/3-upload-model.sh`
        - `PoAIW/llms/Challenger/scripts/4-load-model.sh`
        - `PoAIW/llms/Challenger/scripts/5-set-max-tokens.sh`
        - `PoAIW/llms/Challenger/scripts/6-register-ctrlb-canister.sh`
        - `PoAIW/llms/Challenger/scripts/7-log-pause.sh`
        - `PoAIW/llms/Challenger/scripts/7-log-resume.sh`
        - `PoAIW/llms/Challenger/scripts/balance.sh`
        - `PoAIW/llms/Challenger/scripts/memory.sh`
        - `PoAIW/llms/Challenger/scripts/ready-check.sh`
        - `PoAIW/llms/Challenger/scripts/status.sh`
        - `PoAIW/llms/Challenger/scripts/top-off.sh`


        - `PoAIW/llms/Judge/scripts/3-upload-model.sh`
        - `PoAIW/llms/Judge/scripts/4-load-model.sh`
        - `PoAIW/llms/Judge/scripts/5-set-max-tokens.sh`
        - `PoAIW/llms/Judge/scripts/6-register-ctrlb-canister.sh`
        - `PoAIW/llms/Judge/scripts/7-log-pause.sh`
        - `PoAIW/llms/Judge/scripts/7-log-resume.sh`
        - `PoAIW/llms/Judge/scripts/balance.sh`
        - `PoAIW/llms/Judge/scripts/memory.sh`
        - `PoAIW/llms/Judge/scripts/ready-check.sh`
        - `PoAIW/llms/Judge/scripts/status.sh`
        - `PoAIW/llms/Judge/scripts/top-off.sh`

        ----------------------------------------------------
        Scripts for the Challenger Controller:

        ```bash
        if [ "$NETWORK_TYPE" = "prd" ]; then
            NUM_LLMS_DEPLOYED=...
            NUM_LLMS_ROUND_ROBIN=...
        fi
        ```

        - `PoAIW/src/Challenger/scripts/register-llms.sh`

        - `PoAIW/src/Judge/scripts/register-llms.sh`

    - In case you're adding a NEW LLM, you must manually upload the model:

        - Temporarily update the script: `PoAIW/llms/Challenger/scripts/3-upload-model.sh` or `PoAIW/llms/Judge/scripts/3-upload-model.sh`:
            ```bash
            # Temporarily overwrite `llm_id_star` & `llm_id_end`
            llm_id_start=0                           # TEMPORARILY CHANGE - eg. to: 1
            llm_id_end=$((NUM_LLMS_DEPLOYED - 1))    # TEMPORARILY CHANGE - eg. to: 1

            for i in $(seq $llm_id_start $llm_id_end)
            ```
        - Upload the model for the new LLM
            ```bash
            # from folder: PoAIW/llms/Challenger or PoAIW/llms/Judge
            NETWORK=prd
            ./scripts/3-upload-model.sh --network $NETWORK
            ```
        - IMPORTANT: RESTORE the script: `PoAIW/llms/Challenger/scripts/3-upload-model.sh` or `PoAIW/llms/Judge/scripts/3-upload-model.sh`
            ```bash
            llm_id_start=0
            llm_id_end=$((NUM_LLMS_DEPLOYED - 1))

            for i in $(seq $llm_id_start $llm_id_end)
            ```

    - Once you have deployed new LLMs and uploaded their models, you can do a regular upgrade of the Challenger system:
        ```bash
        # Make sure all patched scripts are restored befpre running the updates
        # From folder: PoAIW
        scripts/deploy-challenger.sh --network $NETWORK --mode upgrade
        scripts/deploy-judge.sh --network $NETWORK --mode upgrade
        ```

    - And re-register everything with the GameState
        ```bash
        # From folder: funnAI
        scripts/scripts-gamestate/register-all.sh --network $NETWORK
        ```

# Update ShareService LLM configuration

todo

    - Re-register all LLMs with the ShareService Agent
        It reads the LLMs from `scripts/canister_ids-$NETWORK.env`
        ```bash
            # from folder: funnAI
            scripts/register_ssllms.sh --network $NETWORK
        ```