<script lang="ts">
  import WalletTable from '../components/WalletTable.svelte';
  
  const transactions = [
    {
      coin: "Internet Computer",
      symbol: "ICP",
      amount: "11.15",
      icon: "/icp-rounded.svg"
    },
    {
      coin: "FunnAI",
      symbol: "FUNN",
      amount: "1110.4",
      icon: "/coin.webp"
    }
  ];
</script>

<div class="container mx-auto px-8 py-8">
  <h1 class="text-2xl text-gray-400 font-bold mb-6">Wallet</h1>
  
  <div class="flex justify-center">
    <div class="w-full md:w-3/4 bg-white card-style p-6 rounded-lg shadow">
      <h2 class="text-xl font-semibold mb-4">Your Assets</h2>
      <WalletTable {transactions} />
    </div>
  </div>
</div>

<script context="module">
  export const Wallet = (props) => {
    return {
      component: Wallet,
      props
    };
  };
</script> 