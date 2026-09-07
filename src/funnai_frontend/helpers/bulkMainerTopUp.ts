import BigNumber from "bignumber.js";
import { MEMO_PAYMENT_PROTOCOL, store, canisterIDLs } from "../stores/store";
import { IcrcService } from "./IcrcService";
import { protocolConfig } from "./token_helpers";
import { createAnonymousActorHelper } from "./utils/actorUtils";
import { getIsProtocolActive } from "./gameState";

let storeState: any;
store.subscribe((value) => {
  storeState = value;
});

export type BulkTopUpStatus = "pending" | "sending" | "confirming" | "success" | "error";

export type BulkTopUpMainer = {
  id: string;
  name?: string;
  originalCanisterInfo?: any;
};

export type BulkTopUpItemResult = {
  id: string;
  name?: string;
  status: BulkTopUpStatus;
  txId?: string;
  error?: string;
};

export type BulkTopUpProgressCallback = (result: BulkTopUpItemResult) => void;

const CMC_CANISTER_ID = "rkp4c-7iaaa-aaaaa-aaaca-cai";
const CYCLES_PER_XDR = new BigNumber("1000000000000");
const FALLBACK_CYCLES_PER_ICP = new BigNumber("10000000000000");

const UI_ONLY_MAINER_FIELDS = [
  "uiStatus",
  "cycleBalance",
  "burnedCycles",
  "cyclesBurnRate",
  "cyclesBurnRateSetting",
  "llmCanisters",
  "llmSetupStatus",
  "hasError",
] as const;

export function getOriginalCanisterInfo(enrichedCanisterInfo: any) {
  if (!enrichedCanisterInfo) return null;
  const originalInfo = { ...enrichedCanisterInfo };
  for (const field of UI_ONLY_MAINER_FIELDS) {
    delete originalInfo[field];
  }
  return originalInfo;
}

export function icpAmountToE8s(amount: string, decimals: number): bigint {
  const [integral, fractional = ""] = amount.split(".");
  const padded = fractional.padEnd(decimals, "0").substring(0, decimals);
  return BigInt(
    new BigNumber(integral || "0")
      .times(new BigNumber(10).pow(decimals))
      .plus(new BigNumber(padded || "0"))
      .toFixed(0),
  );
}

export function formatLedgerError(err: unknown): string {
  if (err instanceof Error) return err.message;
  if (typeof err === "string") return err;
  if (err && typeof err === "object") {
    if ("InsufficientFunds" in err) return "Insufficient ICP balance";
    if ("Duplicate" in err) return "Duplicate transfer — please retry";
    const key = Object.keys(err as object)[0];
    if (key) return key;
  }
  return "Transfer failed";
}

export async function loadIcpCyclesConversionRate(): Promise<BigNumber> {
  try {
    const cmcActor = await createAnonymousActorHelper(CMC_CANISTER_ID, canisterIDLs.cmc);
    const response = await cmcActor.get_icp_xdr_conversion_rate();
    if (!response?.data) {
      throw new Error("Failed to get conversion rate data");
    }
    const xdrRate = Number(response.data.xdr_permyriad_per_icp);
    return new BigNumber(xdrRate).times(CYCLES_PER_XDR).div(10000);
  } catch (error) {
    console.error("Error loading ICP conversion rate:", error);
    return FALLBACK_CYCLES_PER_ICP;
  }
}

export function estimateCyclesFromIcp(
  amount: string,
  conversionRate: BigNumber | null,
  bonusPercent: number,
): { gross: BigNumber; bonus: BigNumber; net: BigNumber } {
  const zero = new BigNumber(0);
  if (!conversionRate || !amount || Number(amount) <= 0) {
    return { gross: zero, bonus: zero, net: zero };
  }
  const gross = conversionRate.times(amount);
  const bonus = bonusPercent > 0 ? gross.times(bonusPercent / 100) : zero;
  return { gross, bonus, net: gross.plus(bonus) };
}

async function topUpSingleMainerWithIcp(params: {
  mainer: BulkTopUpMainer;
  icpToken: FE.Token;
  amountE8s: bigint;
}): Promise<{ txId: string; backendPromise: Promise<any> }> {
  const { mainer, icpToken, amountE8s } = params;

  const mainerAgent =
    storeState.userMainerAgentCanistersInfo?.find(
      (agent: any) => agent.address === mainer.id || agent.id === mainer.id,
    ) || mainer.originalCanisterInfo;

  const cleanMainerAgent = getOriginalCanisterInfo(mainerAgent);
  if (!cleanMainerAgent) {
    throw new Error("mAIner agent not found in user data");
  }

  const result = await IcrcService.transfer(
    icpToken,
    protocolConfig.address,
    amountE8s,
    {
      fee: BigInt(icpToken.fee_fixed),
      memo: MEMO_PAYMENT_PROTOCOL,
    },
  );

  if (!result || typeof result !== "object" || !("Ok" in result)) {
    const err = result && typeof result === "object" && "Err" in result ? result.Err : result;
    throw new Error(formatLedgerError(err));
  }

  const txId = (result as { Ok: bigint | number | string }).Ok?.toString();
  if (!txId) {
    throw new Error("Transfer succeeded but no transaction id was returned");
  }

  if (!storeState.gameStateCanisterActor) {
    throw new Error("Game state canister not available");
  }

  const backendPromise = storeState.gameStateCanisterActor.topUpCyclesForMainerAgent({
    paymentTransactionBlockId: BigInt(txId),
    mainerAgent: cleanMainerAgent,
  });

  return { txId, backendPromise };
}

/**
 * Sends the same ICP amount to every mAIner.
 * Ledger transfers run sequentially (wallet signing + account balance).
 * Protocol credit calls run in parallel via Promise.all.
 */
export async function topUpAllMainersWithIcp(params: {
  mainers: BulkTopUpMainer[];
  amount: string;
  icpToken: FE.Token;
  onProgress?: BulkTopUpProgressCallback;
}): Promise<BulkTopUpItemResult[]> {
  const { mainers, amount, icpToken, onProgress } = params;
  const amountE8s = icpAmountToE8s(amount, icpToken.decimals);
  const results = new Map<string, BulkTopUpItemResult>();

  const emit = (item: BulkTopUpItemResult) => {
    results.set(item.id, item);
    onProgress?.(item);
  };

  const isProtocolActive = await getIsProtocolActive();
  if (!isProtocolActive) {
    throw new Error("Protocol is not active and actions are paused");
  }

  for (const mainer of mainers) {
    emit({ id: mainer.id, name: mainer.name, status: "pending" });
  }

  const backendJobs: Array<Promise<void>> = [];
  let abortRemaining = false;

  for (const mainer of mainers) {
    if (abortRemaining) {
      emit({
        id: mainer.id,
        name: mainer.name,
        status: "error",
        error: "Skipped after a previous transfer failed",
      });
      continue;
    }

    emit({ id: mainer.id, name: mainer.name, status: "sending" });

    try {
      const { txId, backendPromise } = await topUpSingleMainerWithIcp({
        mainer,
        icpToken,
        amountE8s,
      });

      emit({ id: mainer.id, name: mainer.name, status: "confirming", txId });

      backendJobs.push(
        backendPromise
          .then((backendResult: any) => {
            if (backendResult && "Ok" in backendResult) {
              emit({ id: mainer.id, name: mainer.name, status: "success", txId });
              return;
            }
            const errMsg =
              backendResult && "Err" in backendResult
                ? formatLedgerError(backendResult.Err)
                : "Protocol confirmation failed";
            emit({
              id: mainer.id,
              name: mainer.name,
              status: "error",
              txId,
              error: `ICP sent, but protocol credit failed: ${errMsg}`,
            });
          })
          .catch((backendError: unknown) => {
            emit({
              id: mainer.id,
              name: mainer.name,
              status: "error",
              txId,
              error: `ICP sent, but protocol credit failed: ${formatLedgerError(backendError)}`,
            });
          }),
      );
    } catch (error) {
      const message = formatLedgerError(error);
      emit({ id: mainer.id, name: mainer.name, status: "error", error: message });
      if (message.toLowerCase().includes("insufficient")) {
        abortRemaining = true;
      }
    }
  }

  await Promise.all(backendJobs);
  return mainers.map((mainer) => results.get(mainer.id)!);
}
