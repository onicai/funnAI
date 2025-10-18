import {
  canisterIds
} from "../stores/store";

const gameStateCanisterId = canisterIds.gameStateCanisterId;

// Export FUNNAI canister ID for use in other components
export const FUNNAI_CANISTER_ID = "vpyot-zqaaa-aaaaa-qavaq-cai";

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

    canister_id: FUNNAI_CANISTER_ID,
    name: "FUNNAI",
    symbol: "FUNNAI",
    decimals: 8,
    address: FUNNAI_CANISTER_ID,
    fee: 0.00000001,
    fee_fixed: "1",
    token: FUNNAI_CANISTER_ID,
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
  /* {
    canister_id: "4uuff-dyaaa-aaaaj-qnoeq-cai",
    name: "FUNNAIdev",
    symbol: "FUNNAIdev",
    decimals: 8,
    address: "4uuff-dyaaa-aaaaj-qnoeq-cai",
    fee: 0.00000001,
    fee_fixed: "1",
    token: "4uuff-dyaaa-aaaaj-qnoeq-cai",
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
    token_id: 9,
    chain: 'IC',
    total_24h_volume: '0'
  },
  {
    canister_id: "z6s3y-4aaaa-aaaaj-a2bjq-cai",
    name: "FUNNAIdemo",
    symbol: "FUNNAIdemo",
    decimals: 8,
    address: "z6s3y-4aaaa-aaaaj-a2bjq-cai",
    fee: 0.00000001,
    fee_fixed: "1",
    token: "z6s3y-4aaaa-aaaaj-a2bjq-cai",
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
    token_id: 8,
    chain: 'IC',
    total_24h_volume: '0'
  }, */
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
    pools: ["xmiu5-jqaaa-aaaag-qbz7q-cai"], // ckBTC/ICP pool on ICPSwap
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
    name: "ICONFUCIUS on the IC",
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
  },
  { 
    canister_id: "7pail-xaaaa-aaaas-aabmq-cai",
    name: "BOB",
    symbol: "BOB",
    decimals: 8,
    address: "7pail-xaaaa-aaaas-aabmq-cai",
    fee: 0.01,
    fee_fixed: "1000000",
    token: "7pail-xaaaa-aaaas-aabmq-cai",
    icrc1: true,
    icrc2: true,
    icrc3: true,
    pool_symbol: "",
    pools: ["ybilh-nqaaa-aaaag-qkhzq-cai"],
    timestamp: Date.now(),
    metrics: null,
    balance: '0',
    logo_url: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAATlBMVEVHcEwmIh0jHxshHRkfGxYaFxMTEQ4RDwwPDQsLCQgHBgUEAwILCwr////09PPk4+LNzMu6urmmpaSOjYx5eXhiYmFLSkk1NDMgHx8AAACPjrPaAAAADXRSTlMAECI1S2GAnLfO3+z85y7WAAAABFBJREFUeNrFm8tirCAMQEFRHjI+Ac3//+id9nbTwXaSgPYsuyiHV0wYECwa1fXaWDd84qzRfadacQtS9cbBKc7orhGX0vbWw+9YraS4BqUdoBi0EtVpegsEXN/UHXrtgYpR9cbeQMaNCm3W/K0KjYYiTCuK6D2U0gs+rYUKOMXuPlRC82bfQDVsK8goDzXpSof/7rWooTpGEDBwAVYKJNLCJbgG2b6DixgaRvv3G1i4ECdp7dfHEvdffUyN+OOfXPNhUIBiHcdxmqZ5+c/6ZEs1orL0gGJ55GyApkEsQLpAADQOsQDoArF8GbSAZS4UACXOcPcJDIgJYArwJ0FCmUACEk1RCjCVC1jECuQI8NehKRXYgYYjDcAen6QP9g/GR84BRBRlANbHW5Yt7p49BA0wBHLGeUu8ITBcgZxpO+gbQQJCAM/mqbGgRwhQmBIxHDrE549GIn0RWkTspbIDgg6diO7pSQz5QMwhfvw5Z6IkqANgCa/tJw/gEztBkeTPwHLeSBrzscGHgh7wxB+i7zGyYrMm10Lxp5W+s+bAZVGIILC8CRUBG4sUT2Da4RvHwikUeuppUPj5/weOgKamIuHnKY6cKbBZHL5ZAKRogCcQ3gnsyKRAMQUWD9/ZXpITbKncsQTyIYgjq1ru0Zsg7yZ84zUUemyJpDkCebRfmJWaEYYhkMfClXtcYYXlCzzGCJ/EiV2pOlIYyHu6nCUkK6k6GIgCCOawA5aBLIBjTkyBeunxeo/AuKbD+z2eiM0eEPgygdXDF/uSG1w/AjHboeRgMBC34fxL+bNx8lInLFtge1s/BYyA4QpM8MrBWAVWaK5AgIyFPgdG9MA7npoPyEj0ElWLjikQIOegV+m9UEyBWEegIyalY20BJUiRyI+0KdgxBbrhCSweMvZsF2AKE00SyLKh32LhiCrNOo7AeZTJTk9RxamkCPy6wjZ6KG7xBxR5E+ORhSHqEhiwv9b6LYQQw0tCNh1Z+8QZMNhDqvQ4ZUxZ0UbbhJ34xGMPRnLm6OHJESZWViixB5XrL4fjMcawjidu+INKhfgKk5k84WfsAfEJILLAe7zEHtfv5O5H2nG9RBxLEJgjoGjRP9lshL6v6MLQ4n+1Oz7ZP0gphdNeL8u6xXRwf7ezQOBMwAOVAXF5hLAkfekFP1smMB7sAfiiLRTwxTcczb0CVrzSFAlMQKQtuMKRKggYccJwo4AUJ7T3CXTiFM0XmOkTwL9JFB85IysEMHfCEULYtm39Ynkyr/wdwI3IfHrmhcqbbrobuBj7x5daB0m5Vlwf34i3NMOF7bdC/KlBK1A07o7+33+93jV/+8DAyr994qEFka52/CXTOsi4+a2ThkoYKXgoBxUYOsFGaihGy9LXhkVYJUpRFtjYTtSgYyq4rfarU37vy2n1AAS8bkVtZGc84DCdFJcgEY+vnbn4/XnbaevhHKv7VtyB/Hr974ZP3Nf7f1bP/wF/hG2iM81NVQAAAABJRU5ErkJggg==",
    token_type: 'IC',
    token_id: 5,
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
