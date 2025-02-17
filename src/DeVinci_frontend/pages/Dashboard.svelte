<script lang="ts">
  import { store } from "../store";
  import Footer from "../components/Footer.svelte";
  import MainerAccordion from "../components/MainerAccordion.svelte";
</script>

<div class="container mx-auto px-8 py-8">
  <h1 class="text-2xl text-gray-400 font-bold mb-6">My mAIners</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
    <div class="card-style p-4 rounded-lg shadow mb-2">
      <MainerAccordion />
    </div>

    <div class="bg-gray-100 p-6 rounded-lg shadow">
      <h2 class="text-sm font-semibold mb-4">Statistics</h2>
      <div class="card-style p-4 rounded-lg shadow mb-2">
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