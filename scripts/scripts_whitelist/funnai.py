import json
import subprocess
import sys
import pprint
from pathlib import Path
from typing import Dict, Any

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
        cmd = [
            "dfx", "canister", "call", 
            "--network", "ic",
            "--output", "json",
            backend_canister_id,
            "getUsersAdmin"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse the JSON response
        response_json = json.loads(result.stdout)

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