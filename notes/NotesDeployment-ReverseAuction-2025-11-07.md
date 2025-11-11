# mAIners failed to deploy via mAInerCreator

During the reverse auction of Nov 7, 2025 the mAInerCreator correctly created the mAIner canisters and installed the code.
However, during setup (configuration) it failed the health check due to a recently introduced maintenance flag.
And it did not finish all the required configurations.
We fixed it manually with the following steps.

## The mainers

The following 12 mAIners were created.

MAINER=zxmgk-zaaaa-aaaaa-qc6fq-cai
MAINER=zclxh-yiaaa-aaaaa-qc6ga-cai
MAINER=zfkrt-vqaaa-aaaaa-qc6gq-cai
MAINER=zli43-oaaaa-aaaaa-qc6hq-cai
MAINER=3etfk-ryaaa-aaaaa-qc6la-cai
MAINER=3nqow-hqaaa-aaaaa-qc6kq-cai
MAINER=zmj2p-dyaaa-aaaaa-qc6ha-cai
MAINER=3yx73-gyaaa-aaaaa-qc6ja-cai
MAINER=3wvst-5iaaa-aaaaa-qc6ia-cai
MAINER=3ruuh-qqaaa-aaaaa-qc6iq-cai
MAINER=37wzp-laaaa-aaaaa-qc6jq-cai
MAINER=3kric-kiaaa-aaaaa-qc6ka-cai

```bash
# Step 1: Set correct type & register with ShareService
dfx canister call --ic $MAINER setMainerCanisterType '(variant {ShareAgent} )'
dfx canister call --ic $MAINER setShareServiceCanisterId '("rilmv-caaaa-aaaaa-qandq-cai")'
# verify
dfx canister call --ic $MAINER getMainerCanisterType
dfx canister --ic call $MAINER getGameStateCanisterId 
dfx canister --ic call $MAINER health
dfx canister --ic call $MAINER getMaintenanceFlag

# Step 2: Turn maintenance flag off, so health endpoint will work, then upgrade to fix remaining steps
dfx canister --ic stop $MAINER
dfx canister --ic snapshot create $MAINER
dfx canister --ic start $MAINER
dfx canister --ic call $MAINER toggleMaintenanceFlagAdmin
# verify
dfx canister --ic call $MAINER getMaintenanceFlag

# Step 3: Upgrade
dfx canister --ic call r5m5y-diaaa-aaaaa-qanaa-cai upgradeMainerControllerAdmin "(record {canisterAddress = \"$MAINER\" })"

# Verify
dfx canister call --ic $MAINER getMainerCanisterType
dfx canister --ic call $MAINER getGameStateCanisterId 
dfx canister --ic call $MAINER health
```