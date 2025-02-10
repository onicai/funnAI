<script lang="ts">
  import { store } from "../store";
  import Footer from "../components/Footer.svelte";
</script>

<div class="container mx-auto px-4 py-8">
  <h1 class="text-2xl font-bold mb-6">Dashboard</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Add your dashboard content here -->
    <div class="bg-white p-6 rounded-lg shadow">
      <h2 class="text-xl font-semibold mb-4">Welcome</h2>
      <p class="text-gray-600">Start a new chat or continue your previous conversations.</p>
    </div>
  </div>
</div>

<script context="module">
  export const Dashboard = (props) => {
    return {
      component: Dashboard,
      props
    };
  };
</script> 