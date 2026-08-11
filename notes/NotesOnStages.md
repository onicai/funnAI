For development and testing, additional stages have been created, i.e. canisters live on the mainnet.

Process to create another stage:
- Initial reference: https://medium.com/@Catalyze.One/working-with-environments-on-the-internet-computer-59ed3d2a5763
- Go to https://nns.ic0.app/ and log in
- From the burger menu, choose My Canisters
- Click on Create Canister and follow the creation flow (note that you need ICP to pay for the creation and charge the canister with cycles), you may start with 3T cycles (and can top up later)
- Click on the new canister and then on Add Controller
- Go to your local CLI and run: icp identity principal
- Copy the principal returned and paste it into the Add Controller field on the nns app, continue and confirm
- To add the controller via icp-cli: e.g. icp canister update-settings --add-controller <principal> -e development funnai_frontend
- Double-check contollers (via icp-cli) with e.g. icp canister status -e development funnai_frontend
- Copy the id of the new canister
- Paste the canister's id in .icp/data/mappings/<env>.ids.json (under the new entry for the stage, the entry's key needs to match the environment name given in icp.yaml) 
- Create a new environments entry in icp.yaml (with the network's name being the same key as given in canister_ids.json)
- If there are multiple canisters for a stage, create as many canisters as needed (e.g. funnai_backend and funnai_frontend)
- Add the CLI command/s in Readme for the new stage (with the correct network name)
- Make sure that all code relevant for stages/networks has been changed (e.g. search for network and check all relevant results in the project files)
- Run the new CLI command/s in Readme and make sure everything works as expected (just just deploy the new canister/s)
- If you have any other projects depending on the canisters or that the canisters depend on, make sure to handle this accordingly