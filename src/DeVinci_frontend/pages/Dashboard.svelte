<script lang="ts">
  import { store } from "../store";
  import Footer from "../components/Footer.svelte";
  import GalaxyBackground from "../components/GalaxyBackground.svelte";
</script>

<GalaxyBackground />

<div class="container mx-auto px-8 py-8 relative">
  <h1 class="text-2xl font-bold mb-6 text-white">Dashboard</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div class="bg-gray-100/50 backdrop-blur-sm p-6 rounded-lg shadow">
      <h2 class="text-sm font-semibold mb-4">My mAIners</h2>
      <div class="card-style p-4 rounded-lg shadow mb-2 bg-white/90">
        #m1
      </div>
      <div class="card-style p-4 rounded-lg shadow mb-2 bg-white/90">
        #m2
      </div>
    </div>

    <div class="bg-gray-100/50 backdrop-blur-sm p-6 rounded-lg shadow">
      <h2 class="text-sm font-semibold mb-4">Winners</h2>
      <div class="card-style p-4 rounded-lg shadow mb-2 bg-white/90">
        <ul>
          <li>#w1</li>
          <li>#w2</li>
          <li>#w3</li>
        </ul>
      </div>
    </div>

    <div class="bg-gray-100/50 backdrop-blur-sm p-6 rounded-lg shadow">
      <h2 class="text-sm font-semibold mb-4">Statistics</h2>
      <div class="card-style p-4 rounded-lg shadow mb-2 bg-white/90">
        <ul>
          <li>#s1</li>
          <li>#s2</li>
          <li>#s3</li>
        </ul>
      </div>
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