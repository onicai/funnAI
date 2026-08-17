import os
import json
import subprocess
import sys
import pprint
from pathlib import Path
from typing import Dict, Any, List

# Shared icp-cli helpers: unlike `dfx ... --output json`, icp-cli cannot decode a Candid
# response, so decoding happens here via icp-py-core.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "lib"))
import icp_helpers  # noqa: E402

def get_funnai_principals() -> list:
    """
    Query the getUsersAdmin endpoint of the funnai_backend canister on the prd network.
    Returns a list of principals.
    """
    try:
        # Get the backend canister ID from the canister_ids-prd.env file
        env_file = Path(__file__).parent / "../canister_ids-prd.env"
        backend_canister_id = None
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('SUBNET_0_1_BACKEND='):
                        backend_canister_id = line.split('=')[1].strip().strip('"')
                        break
        
        if not backend_canister_id:
            raise ValueError("Could not find SUBNET_0_1_BACKEND in canister_ids-prd.env")
        
        print(f"Querying backend canister: {backend_canister_id}")
        
        # Run the dfx canister call command
        cmd = ["icp", "canister", "call", backend_canister_id, "getUsersAdmin", "()", "-e", "ic"]
        
        print(f"Running command: {' '.join(cmd)}")
        response_json = icp_helpers.call_argv(cmd)

        # Extract the list of principals
        principals = response_json.get('Ok', [])

        return principals
        
    except subprocess.CalledProcessError as e:
        print(f"Error running dfx command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def get_mainer_ownership_data() -> Dict[str, List[str]]:
    """
    Query the getMainerAgentCanistersAdmin endpoint of the GameState canister.
    Returns a dictionary mapping principal -> list of mAIner canister addresses.
    """
    try:
        # Get the GameState canister ID from the canister_ids-prd.env file
        env_file = Path(__file__).parent / "../canister_ids-prd.env"
        gamestate_canister_id = None

        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('SUBNET_0_1_GAMESTATE='):
                        gamestate_canister_id = line.split('=')[1].strip().strip('"')
                        break

        if not gamestate_canister_id:
            raise ValueError("Could not find SUBNET_0_1_GAMESTATE in canister_ids-prd.env")

        print(f"Querying GameState canister: {gamestate_canister_id}")

        # Run the dfx canister call command
        cmd = ["icp", "canister", "call", gamestate_canister_id, "getMainerAgentCanistersAdmin", "()", "-e", "ic"]

        print(f"Running command: {' '.join(cmd)}")
        response_json = icp_helpers.call_argv(cmd)

        # Extract the mAIner data
        mainers_data = response_json.get('Ok', [])

        # Create a mapping of principal -> list of canister addresses
        principal_to_mainers: Dict[str, List[str]] = {}

        for mainer in mainers_data:
            owned_by = mainer.get('ownedBy')
            address = mainer.get('address', '')

            # Only include mAIners with actual addresses (not empty strings)
            if owned_by and address and address != "":
                if owned_by not in principal_to_mainers:
                    principal_to_mainers[owned_by] = []
                principal_to_mainers[owned_by].append(address)

        print(f"Found mAIner ownership data for {len(principal_to_mainers)} principals")
        return principal_to_mainers

    except subprocess.CalledProcessError as e:
        print(f"Error running dfx command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)