import {
  canisterIds
} from "../stores/store";

const gameStateCanisterId = canisterIds.gameStateCanisterId;

const availableTokens: FE.Token[] = [ // TODO
  { 
    /* canister_id: this.toString(data.canister_id),
    name: this.toString(data.name),
    symbol: this.toString(data.symbol),
    decimals: this.toNumber(data.decimals),
    address: this.toString(data.address || data.canister_id),
    fee: this.toNumber(data.fee),
    fee_fixed: this.toString(data.fee_fixed || data.fee),
    token: this.toString(data.token || data.canister_id),
    icrc1: this.toBoolean(data.icrc1),
    icrc2: this.toBoolean(data.icrc2),
    icrc3: this.toBoolean(data.icrc3),
    pool_symbol: this.toString(data.pool_symbol),
    pools: Array.isArray(data.pools) ? data.pools : [],
    timestamp: Date.now(),
    metrics: this.serializeTokenMetrics(data.metrics),
    balance: this.toString(data.balance || '0'),
    logo_url: this.toString(data.logo_url),
    token_type: this.toString(data.token_type || 'IC'),
    token_id: tokenId,
    chain: this.toString(data.chain || 'IC'),
    total_24h_volume: this.toString(data.total_24h_volume || '0') */

    canister_id: "vpyot-zqaaa-aaaaa-qavaq-cai",
    name: "FUNNAI",
    symbol: "FUNNAI",
    decimals: 8,
    address: "vpyot-zqaaa-aaaaa-qavaq-cai",
    fee: 0.0000001,
    fee_fixed: "10",
    token: "vpyot-zqaaa-aaaaa-qavaq-cai",
    icrc1: true,
    icrc2: true,
    icrc3: true,
    pool_symbol: "",
    pools: [],
    timestamp: Date.now(),
    metrics: null,
    balance: '0',
    logo_url: "/coin.webp",
    token_type: 'IC',
    token_id: 1,
    chain: 'IC',
    total_24h_volume: '0'
  },
  { 
    canister_id: "ryjl3-tyaaa-aaaaa-aaaba-cai",
    name: "ICP",
    symbol: "ICP",
    decimals: 8,
    address: "ryjl3-tyaaa-aaaaa-aaaba-cai",
    fee: 0.0001,
    fee_fixed: "10000",
    token: "ryjl3-tyaaa-aaaaa-aaaba-cai",
    icrc1: true,
    icrc2: true,
    icrc3: true,
    pool_symbol: "",
    pools: [],
    timestamp: Date.now(),
    metrics: null,
    balance: '0',
    logo_url: "/icp-rounded.svg",
    token_type: 'IC',
    token_id: 2,
    chain: 'IC',
    total_24h_volume: '0'
  },
  { 
    canister_id: "mxzaz-hqaaa-aaaar-qaada-cai",
    name: "ckBTC",
    symbol: "ckBTC",
    decimals: 8,
    address: "mxzaz-hqaaa-aaaar-qaada-cai",
    fee: 0.0000001,
    fee_fixed: "10",
    token: "mxzaz-hqaaa-aaaar-qaada-cai",
    icrc1: true,
    icrc2: true,
    icrc3: true,
    pool_symbol: "",
    pools: [],
    timestamp: Date.now(),
    metrics: null,
    balance: '0',
    logo_url: "/ckbtc.webp",
    token_type: 'IC',
    token_id: 3,
    chain: 'IC',
    total_24h_volume: '0'
  },
  { 
    canister_id: "5kijx-siaaa-aaaar-qaqda-cai",
    name: "ICONFUCIUS",
    symbol: "ICONFUCIUS",
    decimals: 8,
    address: "5kijx-siaaa-aaaar-qaqda-cai",
    fee: 0.0000001,
    fee_fixed: "10",
    token: "5kijx-siaaa-aaaar-qaqda-cai",
    icrc1: true,
    icrc2: true,
    icrc3: true,
    pool_symbol: "",
    pools: [],
    timestamp: Date.now(),
    metrics: null,
    balance: '0',
    logo_url: "/iconfucius.jpg",
    token_type: 'IC',
    token_id: 4,
    chain: 'IC',
    total_24h_volume: '0'
  }
];

export const fetchTokens = async (options) => {
  return {
    tokens: availableTokens,
    total_count: availableTokens.length,
  };
};

// Protocol configuration
export const protocolConfig = {
  // Funnai account address for payments and top-ups
  // TODO: Change to the actual protocol address
  address: gameStateCanisterId,
  //address: "ciqqv-4iaaa-aaaag-auara-cai", // Game State on Dev stage
  //address: "4tr6r-mqaaa-aaaae-qfcta-cai", // Game State on Demo stage
  // Add other protocol-related configuration here
};
