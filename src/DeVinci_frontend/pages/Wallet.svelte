<script lang="ts">
  
</script>

<div class="container mx-auto px-4 py-8">
  <h1 class="text-2xl font-bold mb-6">Wallet</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Add your dashboard content here -->
    <div class="bg-white card-style w-full p-6 rounded-lg shadow">
      <h2 class="text-xl font-semibold mb-4">Welcome to your wallet</h2>
      <p class="text-gray-600">wallet.</p>
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