<script lang="ts">

  import { theme } from "../stores/store";
  import { ExternalLink, Star, MessageSquare } from "lucide-svelte";
  import { link } from 'svelte-spa-router';
  import Footer from "../components/funnai/Footer.svelte";
  
  // App store data - embedded for reliability
  let storeData = {
    apps: [
      {
        name: "deVinci AI Chat",
        url: "https://funnai.ic0.app/chat",
        description: "Advanced AI chat interface with multiple models, code execution, and document analysis capabilities.",
        thumbnail: "/src/funnai_frontend/assets/chat/devinci1024.webp",
        logo: "/src/funnai_frontend/assets/chat/devinci-logo.svg",
        creator_openchat: "@onicaiHQ",
        creator_x: "@onicaiHQ",
        featured: true
      },
      {
        name: "mAIner Protocol",
        url: "https://funnai.ic0.app/",
        description: "Decentralized AI miner management platform for training and running AI models on the Internet Computer.",
        thumbnail: "/src/funnai_frontend/assets/funnai_512.webp",
        logo: "/src/funnai_frontend/assets/funnai_black.svg",
        creator_openchat: "@onicaiHQ",
        creator_x: "@onicaiHQ",
        featured: true
      },
      {
        name: "Crypto Wallet",
        url: "https://funnai.ic0.app/wallet",
        description: "Secure multi-token wallet for managing ICP, FUNNAI, ckBTC and other tokens on the Internet Computer.",
        thumbnail: "/src/funnai_frontend/assets/icppart.webp",
        logo: "/src/funnai_frontend/assets/icp-rounded.svg",
        creator_openchat: "@onicaiHQ",
        creator_x: "@onicaiHQ",
        featured: false
      },
      {
        name: "Protocol Dashboard",
        url: "https://funnai.ic0.app/dashboard",
        description: "Real-time analytics and metrics for the funnAI ecosystem, including token distribution and miner statistics.",
        thumbnail: "/src/funnai_frontend/assets/ic_logo_hex.svg",
        logo: "/src/funnai_frontend/assets/ic_logo_hex_white.svg",
        creator_openchat: "@onicaiHQ",
        creator_x: "@onicaiHQ",
        featured: false
      },
      {
        name: "Lottery & Gaming",
        url: "https://funnai.ic0.app/lottery",
        description: "Fun lottery and reward system integrated with the funnAI token ecosystem.",
        thumbnail: "/src/funnai_frontend/assets/coin.webp",
        logo: "/src/funnai_frontend/assets/funnai_white.svg",
        creator_openchat: "@onicaiHQ",
        creator_x: "@onicaiHQ",
        featured: false
      },
      {
        name: "OpenChat Community",
        url: "https://oc.app/community/mepna-eqaaa-aaaar-bclua-cai/",
        description: "Join the official funnAI community on OpenChat for discussions, updates, and support.",
        thumbnail: "/src/funnai_frontend/assets/chat/devinci512.webp",
        logo: "/src/funnai_frontend/assets/chat/devinci-logo.svg",
        creator_openchat: "@onicaiHQ",
        creator_x: "@onicaiHQ",
        featured: true
      },
      {
        name: "IC Rocks Explorer",
        url: "https://ic.rocks/",
        description: "Explore the Internet Computer blockchain, view transactions, canisters, and network statistics.",
        thumbnail: "/src/funnai_frontend/assets/ic_logo_hex.svg",
        logo: "/src/funnai_frontend/assets/ic_logo_hex_white.svg",
        creator_openchat: "@ic_rocks",
        creator_x: "@ic_rocks",
        featured: false
      },
      {
        name: "ICPSwap DEX",
        url: "https://app.icpswap.com/",
        description: "Decentralized exchange for trading FUNNAI and other tokens on the Internet Computer.",
        thumbnail: "/src/funnai_frontend/assets/icppart.webp",
        logo: "/src/funnai_frontend/assets/icp-rounded.svg",
        creator_openchat: "@ICPSwap",
        creator_x: "@ICPSwap",
        featured: false
      },
      {
        name: "Internet Identity",
        url: "https://identity.ic0.app/",
        description: "Secure authentication service for Internet Computer applications using WebAuthn.",
        thumbnail: "/src/funnai_frontend/assets/ic_logo_hex.svg",
        logo: "/src/funnai_frontend/assets/ic_logo_hex_white.svg",
        creator_openchat: "@dfinity",
        creator_x: "@dfinity",
        featured: false
      },
      {
        name: "Sonic DEX",
        url: "https://sonic.ooo/",
        description: "High-performance decentralized exchange built on the Internet Computer.",
        thumbnail: "/src/funnai_frontend/assets/coin.webp",
        logo: "/src/funnai_frontend/assets/icp-rounded.svg",
        creator_openchat: "@sonic_ooo",
        creator_x: "@sonic_ooo",
        featured: false
      },
      {
        name: "Distrikt Social",
        url: "https://distrikt.app/",
        description: "Decentralized social media platform built on the Internet Computer.",
        thumbnail: "/src/funnai_frontend/assets/chat/devinci512.webp",
        logo: "/src/funnai_frontend/assets/chat/devinci-logo.svg",
        creator_openchat: "@distrikt",
        creator_x: "@distrikt_app",
        featured: false
      },
      {
        name: "NNS Governance",
        url: "https://nns.ic0.app/",
        description: "Network Nervous System governance interface for the Internet Computer.",
        thumbnail: "/src/funnai_frontend/assets/ic_logo_hex.svg",
        logo: "/src/funnai_frontend/assets/ic_logo_hex_white.svg",
        creator_openchat: "@dfinity",
        creator_x: "@dfinity",
        featured: false
      }
    ]
  };
  
  let isLoading = false;
  let error = null;
  
  // Filtering and search
  let searchTerm = '';
  
  // Reactive filtered apps
  $: filteredApps = storeData.apps.filter(app => {
    const matchesSearch = app.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });
  
  $: featuredApps = storeData.apps.filter(app => app.featured);
  
  function openApp(url: string) {
    if (url.startsWith('http')) {
      // External URL - open in new tab
      window.open(url, '_blank');
    } else {
      // Internal route - use svelte-spa-router navigation
      window.location.hash = '#' + url;
    }
  }
</script>

<div class="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-900">
  <!-- Main Content -->
  <div class="flex-1 p-6 pb-24">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-2">
        funnAI App Store
      </h1>
      <p class="text-lg text-gray-600 dark:text-gray-400">
        Discover amazing funnAI decentralized applications
      </p>
    </div>

    {#if isLoading}
      <!-- Loading State -->
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        <span class="ml-3 text-gray-600 dark:text-gray-400">Loading apps...</span>
      </div>
    {:else if error}
      <!-- Error State -->
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 text-center">
        <p class="text-red-600 dark:text-red-400">Error loading apps: {error}</p>
      </div>
    {:else}
      <!-- Submit Your App Banner -->
      <div class="mb-8 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-2xl border border-purple-200 dark:border-purple-800 p-6">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              🏆 Build & Submit Your App
            </h3>
            <p class="text-gray-600 dark:text-gray-400 text-sm">
              Join the funnAI x CaffeineAI Community Challenge! Build with CaffeineAI, integrate with funnAI, and compete for amazing prizes including mAIners with 40T cycles each! ☕🦜
            </p>
          </div>
          <button
            on:click={() => window.open('https://github.com/onicai/awesome-funnAI-caffeineAI', '_blank')}
            class="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-medium py-3 px-6 rounded-xl transition-all duration-200 flex items-center gap-2 group whitespace-nowrap"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            <span>Submit Your App</span>
            <ExternalLink class="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
          </button>
        </div>
      </div>

      <!-- Search -->
      <div class="mb-8">
        <div class="max-w-md">
          <input
            type="text"
            placeholder="Search apps..."
            bind:value={searchTerm}
            class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
          />
        </div>
      </div>

      <!-- Featured Apps Section -->
      {#if featuredApps.length > 0 && !searchTerm}
        <div class="mb-12">
          <div class="flex items-center gap-2 mb-6">
            <Star class="w-6 h-6 text-yellow-500" />
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Featured Apps</h2>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each featuredApps as app}
              <div class="group relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden">
                <!-- Featured Badge -->
                <div class="absolute top-4 right-4 z-10">
                  <div class="bg-gradient-to-r from-yellow-400 to-yellow-500 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1">
                    <Star class="w-3 h-3" />
                    Featured
                  </div>
                </div>
                
                <!-- App Thumbnail -->
                <div class="relative h-48 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900/30 dark:to-blue-900/30">
                  <img 
                    src={app.thumbnail} 
                    alt={app.name}
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300"></div>
                </div>
                
                <!-- App Info -->
                <div class="p-6">
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center gap-3">
                      {#if app.logo}
                        <img 
                          src={app.logo} 
                          alt={app.name}
                          class="w-10 h-10 rounded-lg border border-gray-200 dark:border-gray-600"
                        />
                      {/if}
                      <div>
                        <h3 class="text-xl font-semibold text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors duration-200">
                          {app.name}
                        </h3>
                      </div>
                    </div>
                  </div>
                  
                  <p class="text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                    {app.description}
                  </p>
                  
                  <!-- Creator Info -->
                  <div class="flex items-center gap-4 mb-4 text-sm text-gray-500 dark:text-gray-400">
                    <div class="flex items-center gap-1">
                      <MessageSquare class="w-4 h-4" />
                      <span>{app.creator_openchat}</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                      </svg>
                      <span>{app.creator_x}</span>
                    </div>
                  </div>
                  
                  <!-- Launch Button -->
                  <button
                    on:click={() => openApp(app.url)}
                    class="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 group"
                  >
                    <span>Launch App</span>
                    <ExternalLink class="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
                  </button>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- All Apps Section -->
      <div>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
            All Apps
          </h2>
          <span class="text-gray-500 dark:text-gray-400">
            {filteredApps.length} app{filteredApps.length !== 1 ? 's' : ''}
          </span>
        </div>

        {#if filteredApps.length === 0}
          <!-- Empty State -->
          <div class="text-center py-12">
            <div class="w-20 h-20 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
              <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">No apps found</h3>
            <p class="text-gray-500 dark:text-gray-400">Try adjusting your search or filter criteria</p>
          </div>
        {:else}
          <!-- Apps Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {#each filteredApps as app}
              <div class="group bg-white dark:bg-gray-800 rounded-xl shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 overflow-hidden">
                <!-- App Thumbnail -->
                <div class="relative h-32 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800">
                  <img 
                    src={app.thumbnail} 
                    alt={app.name}
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  {#if app.featured}
                    <div class="absolute top-2 right-2">
                      <Star class="w-4 h-4 text-yellow-500" fill="currentColor" />
                    </div>
                  {/if}
                </div>
                
                <!-- App Info -->
                <div class="p-4">
                  <div class="flex items-center gap-2 mb-2">
                    {#if app.logo}
                      <img 
                        src={app.logo} 
                        alt={app.name}
                        class="w-8 h-8 rounded border border-gray-200 dark:border-gray-600"
                      />
                    {/if}
                    <h3 class="font-semibold text-gray-900 dark:text-white text-sm group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors duration-200">
                      {app.name}
                    </h3>
                  </div>
                  
                  <p class="text-gray-600 dark:text-gray-400 text-xs mb-3 line-clamp-2">
                    {app.description}
                  </p>
                  
                  <!-- Creator Info -->
                  <div class="flex items-center gap-3 mb-3 text-xs text-gray-500 dark:text-gray-400">
                    <div class="flex items-center gap-1">
                      <MessageSquare class="w-3 h-3" />
                      <span>{app.creator_openchat}</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                      </svg>
                      <span>{app.creator_x}</span>
                    </div>
                  </div>
                  
                  <div class="flex items-center justify-end">
                    <button
                      on:click={() => openApp(app.url)}
                      class="bg-purple-600 hover:bg-purple-700 text-white text-xs font-medium py-1.5 px-3 rounded-lg transition-colors duration-200 flex items-center gap-1"
                    >
                      <span>Launch</span>
                      <ExternalLink class="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Footer -->
  <Footer />
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>