<script lang="ts">
  import { theme } from "../stores/store";
</script>

<div class="w-full min-h-screen dark:bg-gray-900 pb-8">
  <div class="container mx-auto py-8 px-4 max-w-6xl">
    <h1 class="text-4xl font-fredoka font-bold mb-8 dark:text-white">Brand Guidelines</h1>
    
    <section class="mb-12">
      <h2 class="text-2xl font-fredoka font-semibold mb-4 dark:text-white">Logotype</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 flex flex-col items-center">
          <h3 class="text-xl font-medium mb-4 dark:text-white">Light Theme</h3>
          <img src="/funnai_black.svg" alt="FunnAI Light Logo" class="h-24 mb-4" />
          <div class="text-sm text-gray-600 dark:text-gray-300 mt-2">
            <p>Format: SVG</p>
            <p>Usage: Light backgrounds</p>
          </div>
        </div>
        <div class="bg-gray-800 shadow-md rounded-lg p-6 flex flex-col items-center">
          <h3 class="text-xl font-medium mb-4 text-white">Dark Theme</h3>
          <img src="/funnai_white.svg" alt="FunnAI Dark Logo" class="h-24 mb-4" />
          <div class="text-sm text-gray-300 mt-2">
            <p>Format: SVG</p>
            <p>Usage: Dark backgrounds</p>
          </div>
        </div>
      </div>
    </section>

    <section class="mb-12">
      <h2 class="text-2xl font-fredoka font-semibold mb-4 dark:text-white">Logo Icon</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 flex flex-col items-center">
          <h3 class="text-xl font-medium mb-4 dark:text-white">Favicon</h3>
          <img src="/coin.webp" alt="FunnAI Favicon" class="h-16 mb-4" />
          <div class="text-sm text-gray-600 dark:text-gray-300 mt-2">
            <p>Format: WebP</p>
            <p>Usage: Browser tabs, bookmarks</p>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 flex flex-col items-center">
          <h3 class="text-xl font-medium mb-4 dark:text-white">App Icon</h3>
          <img src="/coin.webp" alt="FunnAI App Icon" class="h-16 mb-4" />
          <div class="text-sm text-gray-600 dark:text-gray-300 mt-2">
            <p>Format: WebP</p>
            <p>Usage: Mobile apps, shortcuts</p>
          </div>
        </div>
      </div>
    </section>

    <section class="mb-12">
      <h2 class="text-2xl font-fredoka font-semibold mb-4 dark:text-white">Colors</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        <!-- Primary Colors -->
        <div class="color-card">
          <div class="h-24 bg-gray-900 rounded-t-lg"></div>
          <div class="p-4 bg-white dark:bg-gray-800 rounded-b-lg shadow-md dark:text-white">
            <h3 class="font-medium">Primary Dark</h3>
            <p class="text-sm text-gray-600 dark:text-gray-300">HEX: #111827</p>
            <p class="text-sm text-gray-600 dark:text-gray-300">RGB: 17, 24, 39</p>
            <p class="text-sm text-gray-600 dark:text-gray-300">Tailwind: gray-900</p>
          </div>
        </div>
        <div class="color-card">
          <div class="h-24 bg-gray-800 rounded-t-lg"></div>
          <div class="p-4 bg-white dark:bg-gray-800 rounded-b-lg shadow-md dark:text-white">
            <h3 class="font-medium">Secondary Dark</h3>
            <p class="text-sm text-gray-600 dark:text-gray-300">HEX: #1f2937</p>
            <p class="text-sm text-gray-600 dark:text-gray-300">RGB: 31, 41, 55</p>
            <p class="text-sm text-gray-600 dark:text-gray-300">Tailwind: gray-800</p>
          </div>
        </div>
        <div class="color-card">
          <div class="h-24 bg-white rounded-t-lg border"></div>
          <div class="p-4 bg-white dark:bg-gray-800 rounded-b-lg shadow-md dark:text-white">
            <h3 class="font-medium">Primary Light</h3>
            <p class="text-sm text-gray-600 dark:text-gray-300">HEX: #ffffff</p>
            <p class="text-sm text-gray-600 dark:text-gray-300">RGB: 255, 255, 255</p>
            <p class="text-sm text-gray-600 dark:text-gray-300">Tailwind: white</p>
          </div>
        </div>
        
        <!-- Additional Colors -->
        <div class="color-card">
          <div class="h-24 rounded-t-lg" style="background-color: #FFC943;"></div>
          <div class="p-4 bg-white dark:bg-gray-800 rounded-b-lg shadow-md dark:text-white">
            <h3 class="font-medium">Gold</h3>
            <p class="text-sm text-gray-600 dark:text-gray-300">HEX: #FFC943</p>
            <p class="text-sm text-gray-600 dark:text-gray-300">RGB: 255, 201, 67</p>
          </div>
        </div>
        <div class="color-card">
          <div class="h-24 rounded-t-lg" style="background-color: #FF223E;"></div>
          <div class="p-4 bg-white dark:bg-gray-800 rounded-b-lg shadow-md dark:text-white">
            <h3 class="font-medium">Red</h3>
            <p class="text-sm text-gray-600 dark:text-gray-300">HEX: #FF223E</p>
            <p class="text-sm text-gray-600 dark:text-gray-300">RGB: 255, 34, 62</p>
          </div>
        </div>
        <div class="color-card">
          <div class="h-24 rounded-t-lg" style="background-color: #29CCFD;"></div>
          <div class="p-4 bg-white dark:bg-gray-800 rounded-b-lg shadow-md dark:text-white">
            <h3 class="font-medium">Blue</h3>
            <p class="text-sm text-gray-600 dark:text-gray-300">HEX: #29CCFD</p>
            <p class="text-sm text-gray-600 dark:text-gray-300">RGB: 41, 204, 253</p>
          </div>
        </div>
        <div class="color-card">
          <div class="h-24 rounded-t-lg" style="background-color: #8475cb;"></div>
          <div class="p-4 bg-white dark:bg-gray-800 rounded-b-lg shadow-md dark:text-white">
            <h3 class="font-medium">Purple</h3>
            <p class="text-sm text-gray-600 dark:text-gray-300">HEX: #8475cb</p>
            <p class="text-sm text-gray-600 dark:text-gray-300">RGB: 132, 117, 203</p>
          </div>
        </div>
      </div>
    </section>

    <section class="mb-12">
      <h2 class="text-2xl font-fredoka font-semibold mb-4 dark:text-white">Typography</h2>
      <div class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h3 class="text-xl font-medium mb-4 dark:text-white">Primary Font: Fredoka</h3>
        <p class="font-fredoka text-4xl font-bold mb-2 dark:text-white">Aa Bb Cc 123</p>
        <p class="font-fredoka text-2xl font-semibold mb-2 dark:text-white">Aa Bb Cc 123</p>
        <p class="font-fredoka text-xl font-medium mb-2 dark:text-white">Aa Bb Cc 123</p>
        <p class="font-fredoka text-lg font-regular mb-2 dark:text-white">Aa Bb Cc 123</p>
        <p class="font-fredoka text-base font-light mb-4 dark:text-white">Aa Bb Cc 123</p>
        
        <div class="text-sm text-gray-600 dark:text-gray-300 mt-4">
          <p>Primary Font: Fredoka</p>
          <p>Weights: Light (300), Regular (400), Medium (500), Semibold (600), Bold (700)</p>
          <p>Usage: Headings, Brand Elements, UI Accents</p>
        </div>

        <h3 class="text-xl font-medium mb-4 mt-8 dark:text-white">Secondary Font: General Sans-Serif</h3>
        <p class="font-sans text-4xl font-bold mb-2 dark:text-white">Aa Bb Cc 123</p>
        <p class="font-sans text-2xl font-semibold mb-2 dark:text-white">Aa Bb Cc 123</p>
        <p class="font-sans text-xl font-medium mb-2 dark:text-white">Aa Bb Cc 123</p>
        <p class="font-sans text-lg font-normal mb-2 dark:text-white">Aa Bb Cc 123</p>
        <p class="font-sans text-base font-light mb-4 dark:text-white">Aa Bb Cc 123</p>
        
        <div class="text-sm text-gray-600 dark:text-gray-300 mt-4">
          <p>Secondary Font: General Sans-Serif</p>
          <p>Weights: Light (300), Regular (400), Medium (500), Semibold (600), Bold (700)</p>
          <p>Usage: Body text, UI Elements, Secondary Content</p>
        </div>
      </div>
    </section>

    <section class="mb-12">
      <h2 class="text-2xl font-fredoka font-semibold mb-4 dark:text-white">Gradients</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="h-48 rounded-lg shadow-md bg-[radial-gradient(circle_at_center,_#e6e9f0,_#fafbfc,_#dfe7fd)]">
          <div class="p-4">
            <h3 class="text-xl font-medium mb-2">Light Theme Gradient</h3>
            <p class="text-sm text-gray-700">radial-gradient(circle at center, #e6e9f0, #fafbfc, #dfe7fd)</p>
            <p class="text-sm text-gray-700 mt-1">Usage: Sidebar background in light mode</p>
          </div>
        </div>
        <div class="h-48 rounded-lg shadow-md bg-[radial-gradient(circle_at_center,_#1f2937,_#111827,_#1e293b)]">
          <div class="p-4">
            <h3 class="text-xl font-medium mb-2 text-white">Dark Theme Gradient</h3>
            <p class="text-sm text-gray-300">radial-gradient(circle at center, #1f2937, #111827, #1e293b)</p>
            <p class="text-sm text-gray-300 mt-1">Usage: Sidebar background in dark mode</p>
          </div>
        </div>
        <div class="h-48 rounded-lg shadow-md bg-gradient-to-br from-[#29CCFD] to-[#1D4ED8]">
          <div class="p-4">
            <h3 class="text-xl font-medium mb-2 text-white">Blue Gradient</h3>
            <p class="text-sm text-gray-100">bg-gradient-to-br from-[#29CCFD] to-[#1D4ED8]</p>
            <p class="text-sm text-gray-100 mt-1">Usage: Call-to-action elements, feature backgrounds</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</div>

<style>
  .color-card {
    border-radius: 0.5rem;
    overflow: hidden;
    transition: transform 0.2s;
  }
  
  .color-card:hover {
    transform: translateY(-4px);
  }
</style> 