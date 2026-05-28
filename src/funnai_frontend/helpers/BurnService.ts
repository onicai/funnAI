import { store } from "../stores/store";
import { get } from "svelte/store";
import BigNumber from "bignumber.js";

export interface TotalBurnedData {
  totalBurnedE8s: bigint;
  totalBurnedFunnai: string;
  lastScannedBlock: bigint;
  lastScanTimestampNs: bigint;
}

export class BurnService {
  static async getTotalBurned(): Promise<TotalBurnedData> {
    const storeValue = get(store);
    if (!storeValue.apiCanisterActor) {
      throw new Error("API canister actor not available");
    }

    const result = await storeValue.apiCanisterActor.getTotalBurned();

    if ("Err" in result) {
      throw new Error(`getTotalBurned failed: ${JSON.stringify(result.Err)}`);
    }

    const record = result.Ok;
    const totalBurnedFunnai = new BigNumber(record.totalBurnedE8s.toString())
      .dividedBy(new BigNumber(10).pow(8))
      .toFormat(2);

    return {
      totalBurnedE8s: record.totalBurnedE8s,
      totalBurnedFunnai,
      lastScannedBlock: record.lastScannedBlock,
      lastScanTimestampNs: record.lastScanTimestampNs,
    };
  }
}
