import { Principal } from "@dfinity/principal";
import { AccountIdentifier, SubAccount } from "@dfinity/ledger-icp";

export interface AccountIds {
  subaccount: string;
  main: string;
}

export function getAccountIds(
  principalStr: string,
  rawSubaccount: any
): AccountIds {
  try {
    const principal = Principal.fromText(principalStr);

    // Create account ID with provided subaccount
    const subAccount = convertToSubaccount(rawSubaccount);
    const subaccountId = AccountIdentifier.fromPrincipal({
      principal,
      subAccount,
    }).toHex();

    // Create account ID with main (zero) subaccount
    const mainAccountId = AccountIdentifier.fromPrincipal({
      principal,
      subAccount: undefined,
    }).toHex();

    return {
      subaccount: subaccountId,
      main: mainAccountId,
    };
  } catch (error) {
    console.error("Error creating account identifier:", error);
    return {
      subaccount: "",
      main: "",
    };
  }
}

function convertToSubaccount(raw: any): SubAccount | undefined {
  try {
    if (!raw) return undefined;

    if (raw instanceof SubAccount) return raw;

    let bytes: Uint8Array;
    if (raw instanceof Uint8Array) {
      bytes = raw;
    } else if (Array.isArray(raw)) {
      bytes = new Uint8Array(raw);
    } else if (typeof raw === "number") {
      bytes = new Uint8Array(32).fill(0);
      bytes[31] = raw;
    } else {
      return undefined;
    }

    if (bytes.length !== 32) {
      const paddedBytes = new Uint8Array(32).fill(0);
      paddedBytes.set(bytes.slice(0, 32));
      bytes = paddedBytes;
    }

    const subAccountResult = SubAccount.fromBytes(bytes);
    if (subAccountResult instanceof Error) {
      throw subAccountResult;
    }
    return subAccountResult;
  } catch (error) {
    console.error("Error converting subaccount:", error);
    return undefined;
  }
}


export function getPrincipalString(principal: string | Principal): string {
  return typeof principal === "string" ? principal : principal?.toText?.() || "";
}

/**
 * The anonymous principal on the Internet Computer (2vxsx-fae).
 * This is the default principal when not authenticated.
 */
export const ANONYMOUS_PRINCIPAL_TEXT = "2vxsx-fae";

/**
 * Checks if a principal is the anonymous principal (2vxsx-fae).
 * IMPORTANT: Never display the anonymous principal as a user's address,
 * as users might accidentally send funds to it.
 * 
 * @param principal - A Principal object or string representation
 * @returns true if the principal is anonymous, false otherwise
 */
export function isAnonymousPrincipal(principal: string | Principal | null | undefined): boolean {
  if (!principal) return true; // null/undefined treated as anonymous
  
  try {
    if (typeof principal === "string") {
      // Check for common anonymous identifiers
      if (principal === "" || principal === "anonymous" || principal === ANONYMOUS_PRINCIPAL_TEXT) {
        return true;
      }
      // Try to parse and use the built-in isAnonymous check
      const principalObj = Principal.fromText(principal);
      return principalObj.isAnonymous();
    }
    
    // Principal object - use built-in method
    return principal.isAnonymous();
  } catch (error) {
    // If parsing fails, consider it anonymous (don't display invalid principals)
    console.warn("Error checking if principal is anonymous:", error);
    return true;
  }
}

/**
 * Checks if a principal is valid (non-null, non-anonymous, and properly formatted).
 * Use this before displaying any principal to users.
 * 
 * @param principal - A Principal object or string representation
 * @returns true if the principal is valid for display, false otherwise
 */
export function isValidUserPrincipal(principal: string | Principal | null | undefined): boolean {
  return !isAnonymousPrincipal(principal);
} 