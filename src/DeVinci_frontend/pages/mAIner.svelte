<script lang="ts">
  import { store } from "../store";
</script>

<div class="container mx-auto h-lvh p-8 bg-[radial-gradient(circle_at_center,_#300030,_#170017,_#0c000c)]">
  <h1 class="text-2xl font-bold mb-6 text-gray-100">mAIner</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Add your dashboard content here -->
    <div class="bg-gray-100/50  p-6 rounded-lg shadow">
      <h2 class="text-sm font-semibold mb-4">Activity feed</h2>
      <div class="card-style p-4 rounded-lg shadow mb-2">
        <ul>
          <li>#s1</li>
          <li>#s2</li>
          <li>#s3</li>
        </ul>
      </div>
    </div>

    <div class="bg-gray-100/50 p-6 rounded-lg shadow">
      <h2 class="text-sm font-semibold mb-4">Flags</h2>
      <div class="card-style p-4 rounded-lg shadow mb-2">
        <ul>
          <li>#s1</li>
          <li>#s2</li>
          <li>#s3</li>
        </ul>
      </div>
    </div>

    <div class="bg-gray-100/50 p-6 rounded-lg shadow">
      <h2 class="text-sm font-semibold mb-4">Stats</h2>
      <div class="card-style p-4 rounded-lg shadow mb-2">
        <ul>
          <li>#s1</li>
          <li>#s2</li>
          <li>#s3</li>
        </ul>
      </div>
    </div>

    <div class="bg-gray-100/50 p-6 rounded-lg shadow">
      <h2 class="text-sm font-semibold mb-4">Top up cycles</h2>
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