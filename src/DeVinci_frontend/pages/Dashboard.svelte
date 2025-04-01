<script lang="ts">
  import MainerAccordion from "../components/MainerAccordion.svelte";
  import MainerFeed from "../components/MainerFeed.svelte";
  import CyclesDisplay from "../components/CyclesDisplay.svelte";
  import WheelOfFortune from "../components/WheelOfFortune.svelte";
  import Footer from "../components/Footer.svelte";
</script>

<div class="h-[calc(100vh-42px)] flex flex-col">
  <div class="container mx-auto px-8 py-8 flex-grow overflow-auto">
    <WheelOfFortune />
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
      <div class="card-style bg-white p-6 rounded-lg shadow mb-2">
        <MainerAccordion />
      </div>
      <div class="card-style bg-white p-4 rounded-lg shadow mb-2">
        <CyclesDisplay cycles={21246900000000} />
        <MainerFeed />
      </div>
    </div>
  </div>
  <Footer />
</div>

<script context="module">
  export const Dashboard = (props) => {
    return {
      component: Dashboard,
      props
    };
  };
</script> 