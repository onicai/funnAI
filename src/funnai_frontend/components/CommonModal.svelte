<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { browser } from "../stores/store";
  import Panel from "./Panel.svelte";
  import { fade } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import Portal from "svelte-portal";
  import { X } from "lucide-svelte";
  import { modalStack } from "../stores/modalStore";

  // Props
  export let isOpen: boolean = false;
  export let modalKey: string = Math.random().toString(36).substr(2, 9);
  export let title: string = ""; // Plain text only (HTML disabled for XSS protection)
  export let variant: "solid" | "transparent" = "solid";
  export let width: string = "600px";
  export let height: string = "auto";
  export let minHeight: string = "auto";
  export let onClose: () => void = () => {};
  export let loading: boolean = false;
  export let closeOnEscape: boolean = true;
  export let closeOnClickOutside: boolean = true;
  export let className: string = "";
  export let isPadded: boolean = false;
  export let target: string = "#portal-target";

  // State
  let isMobile: boolean = false;
  let modalWidth: string = width;
  let modalHeight: string = height;
  let startX: number = 0;
  let startY: number = 0;
  let currentX: number = 0;
  let isDragging: boolean = false;
  let dragAxisLocked: "x" | "y" | null = null;
  let zIndex: number = 99999;
  let modalElement: HTMLDivElement;
  let previousBodyStyles: {
    overflow: string;
    position: string;
    top: string;
    width: string;
    left: string;
    right: string;
  } | null = null;
  let lockedScrollY = 0;
  let scrollLocked = false;

  const SLIDE_THRESHOLD = 100;
  const AXIS_LOCK_PX = 8;

  function lockBodyScroll() {
    if (!browser || scrollLocked) return;

    lockedScrollY = window.scrollY || window.pageYOffset || 0;
    previousBodyStyles = {
      overflow: document.body.style.overflow,
      position: document.body.style.position,
      top: document.body.style.top,
      width: document.body.style.width,
      left: document.body.style.left,
      right: document.body.style.right,
    };

    // iOS Safari ignores overflow:hidden on body while a fixed modal is open.
    // Pinning the body prevents the page (and modal compositing) from scrolling underneath.
    document.body.style.overflow = "hidden";
    document.body.style.position = "fixed";
    document.body.style.top = `-${lockedScrollY}px`;
    document.body.style.left = "0";
    document.body.style.right = "0";
    document.body.style.width = "100%";
    document.documentElement.style.overflow = "hidden";
    scrollLocked = true;
  }

  function unlockBodyScroll() {
    if (!browser || !scrollLocked) return;

    if (previousBodyStyles) {
      document.body.style.overflow = previousBodyStyles.overflow;
      document.body.style.position = previousBodyStyles.position;
      document.body.style.top = previousBodyStyles.top;
      document.body.style.width = previousBodyStyles.width;
      document.body.style.left = previousBodyStyles.left;
      document.body.style.right = previousBodyStyles.right;
      previousBodyStyles = null;
    } else {
      document.body.style.overflow = "";
      document.body.style.position = "";
      document.body.style.top = "";
      document.body.style.width = "";
      document.body.style.left = "";
      document.body.style.right = "";
    }
    document.documentElement.style.overflow = "";
    window.scrollTo(0, lockedScrollY);
    scrollLocked = false;
  }

  function syncModalStack(open: boolean) {
    if (open) {
      modalStack.update((stack) => {
        if (stack[modalKey]?.active) return stack;
        return {
          ...stack,
          [modalKey]: { active: true, timestamp: Date.now() },
        };
      });
      lockBodyScroll();
    } else {
      modalStack.update((stack) => {
        if (!(modalKey in stack)) return stack;
        const { [modalKey]: _, ...rest } = stack;
        return rest;
      });
      unlockBodyScroll();
    }
  }

  $: syncModalStack(isOpen);

  $: if (browser) {
    isMobile = typeof window !== "undefined" && window.innerWidth <= 768;
    modalWidth = isMobile ? "100%" : width;
    modalHeight = isMobile ? "auto" : height;
  }

  onMount(() => {
    if (!browser) return;

    const updateDimensions = () => {
      isMobile = window.innerWidth <= 768;
      modalWidth = isMobile ? "100%" : width;
      modalHeight = isMobile ? "auto" : height;
    };
    updateDimensions();
    window.addEventListener("resize", updateDimensions);

    const unsubscribe = modalStack.subscribe((stack) => {
      const modalEntries = Object.entries(stack);
      if (modalEntries.length === 0) return;

      modalEntries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      const currentIndex = modalEntries.findIndex(([key]) => key === modalKey);
      if (currentIndex !== -1) {
        zIndex = 99999 + currentIndex * 10;
      }
    });

    return () => {
      window.removeEventListener("resize", updateDimensions);
      unsubscribe();
      if (modalElement) {
        modalElement.style.transform = "";
        modalElement.style.transition = "";
      }
    };
  });

  onDestroy(() => {
    modalStack.update((stack) => {
      const { [modalKey]: _, ...rest } = stack;
      return rest;
    });
    unlockBodyScroll();
    isDragging = false;
    currentX = 0;
    dragAxisLocked = null;
  });

  // Swipe-to-close ONLY from the drag handle — never from modal body/content.
  // Attaching touch handlers to the whole panel was stealing vertical scroll on mobile
  // and applying translateX, which made the top-up form appear to vanish while scrolling.
  function handleDragStart(event: TouchEvent | MouseEvent) {
    if (!isMobile) return;

    isDragging = true;
    dragAxisLocked = null;
    if ("touches" in event) {
      startX = event.touches[0].clientX;
      startY = event.touches[0].clientY;
    } else {
      startX = event.clientX;
      startY = event.clientY;
    }
    currentX = 0;
    if (modalElement) {
      modalElement.style.transition = "none";
    }
  }

  function handleDragMove(event: TouchEvent | MouseEvent) {
    if (!isMobile || !isDragging || !modalElement) return;

    const x = "touches" in event ? event.touches[0].clientX : event.clientX;
    const y = "touches" in event ? event.touches[0].clientY : event.clientY;
    const dx = x - startX;
    const dy = y - startY;

    if (!dragAxisLocked) {
      if (Math.abs(dx) < AXIS_LOCK_PX && Math.abs(dy) < AXIS_LOCK_PX) return;
      dragAxisLocked = Math.abs(dx) > Math.abs(dy) ? "x" : "y";
      if (dragAxisLocked === "y") {
        // Vertical gesture on the handle — don't hijack it as a dismiss swipe
        isDragging = false;
        dragAxisLocked = null;
        modalElement.style.transform = "";
        return;
      }
    }

    if (dragAxisLocked !== "x") return;

    if ("touches" in event) {
      event.preventDefault();
    }

    currentX = dx;
    const resistance = 0.5;
    modalElement.style.transform = `translateX(${currentX * resistance}px)`;
  }

  function handleDragEnd() {
    if (!isMobile || !modalElement) return;
    if (!isDragging) {
      dragAxisLocked = null;
      return;
    }

    isDragging = false;
    dragAxisLocked = null;
    modalElement.style.transition = "transform 0.3s ease-out";

    if (Math.abs(currentX) > SLIDE_THRESHOLD) {
      modalElement.style.transform = `translateX(${Math.sign(currentX) * window.innerWidth}px)`;
      setTimeout(handleClose, 300);
    } else {
      modalElement.style.transform = "translateX(0)";
    }
  }

  function handleClose(event?: Event) {
    if (event) {
      event.stopPropagation();
    }
    modalStack.update((stack) => {
      const { [modalKey]: _, ...rest } = stack;
      return rest;
    });
    unlockBodyScroll();
    isOpen = false;
    onClose();
  }

  function handleBackdropClick(event: MouseEvent) {
    event.stopPropagation();
    if (event.target === event.currentTarget && closeOnClickOutside) {
      handleClose();
    }
  }

  function handleEscape(event: KeyboardEvent) {
    if (event.key === "Escape" && closeOnEscape) {
      const modalEntries = Object.entries($modalStack);
      if (modalEntries.length === 0) return;

      modalEntries.sort((a, b) => a[1].timestamp - b[1].timestamp);

      if (modalEntries[modalEntries.length - 1][0] === modalKey) {
        handleClose();
      }
    }
  }
</script>

<svelte:window on:keydown={handleEscape} />
<Portal target={target}>
  {#if isOpen}
    <div
      class="fixed inset-0 grid place-items-center modal-root"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      style="z-index: {zIndex};"
    >
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <div
        class="fixed inset-0 bg-black/70"
        on:click={handleBackdropClick}
        style="z-index: {zIndex};"
        transition:fade={{ duration: 120, easing: cubicOut }}
      />

      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <div
        bind:this={modalElement}
        class="relative max-w-full {isPadded ? 'px-4' : ''} max-h-[min(calc(100vh-40px),calc(100dvh-40px))] flex flex-col overflow-hidden"
        style="width: {modalWidth}; z-index: {zIndex + 1};"
        on:click|stopPropagation
        transition:fade={{ duration: 150, delay: 100, easing: cubicOut }}
      >
        <Panel
          variant="solid"
          width="100%"
          height="100%"
          className="flex flex-col overflow-hidden modal-panel {className}"
        >
          <div
            class="modal-content flex flex-col overflow-hidden"
            style="min-height: {minHeight};"
          >
            {#if loading}
              <div class="loading-overlay">
                <div class="spinner"></div>
              </div>
            {/if}

            <!-- Mobile dismiss handle only — keeps content scroll free of transform hijacking -->
            <div
              class="drag-handle"
              role="button"
              tabindex="0"
              aria-label="Drag to dismiss"
              on:touchstart|stopPropagation={handleDragStart}
              on:touchmove|stopPropagation={handleDragMove}
              on:touchend|stopPropagation={handleDragEnd}
              on:touchcancel|stopPropagation={handleDragEnd}
              on:mousedown|stopPropagation={handleDragStart}
              on:mousemove|stopPropagation={handleDragMove}
              on:mouseup|stopPropagation={handleDragEnd}
              on:mouseleave|stopPropagation={handleDragEnd}
            ></div>

            <header
              class="flex justify-between items-center flex-shrink-0 pb-4"
            >
              <div class="flex-grow">
                <slot name="title">
                  <h2 class="text-lg font-semibold modal-title text-gray-900 dark:text-gray-100">
                    {#if typeof title === "string"}
                      {title}
                    {/if}
                  </h2>
                </slot>
              </div>
              <button
                class="!flex !items-center hover:text-red-600 !border-0 !shadow-none group relative ml-2 text-gray-600 hover:text-red-400 dark:text-gray-300 dark:hover:text-red-400"
                on:click={(e) => handleClose(e)}
                aria-label="Close modal"
              >
                <X size={18} />
              </button>
            </header>

            <div class="modal-scroll flex-1 overflow-y-auto overscroll-contain scrollbar-custom min-h-0">
              <slot></slot>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  {/if}
</Portal>

<style scoped>
  .action-button {
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s ease;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    width: 40px;
  }

  .drag-handle {
    flex-shrink: 0;
    width: 44px;
    height: 5px;
    margin: 4px auto 12px;
    border-radius: 9999px;
    background: rgba(156, 163, 175, 0.45);
    touch-action: none;
    cursor: grab;
  }

  .modal-scroll {
    touch-action: pan-y;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
  }

  :global(.modal-content) {
    max-height: inherit;
    height: 100%;
  }

  :global(#portal-target) {
    position: fixed;
    inset: 0;
    z-index: 100000;
    pointer-events: none;
  }

  :global(#portal-target > *) {
    pointer-events: auto;
  }

  :global(.modal-panel) {
    position: relative;
  }

  .modal-root {
    /* Avoid rubber-band scroll chaining into the page on iOS */
    overscroll-behavior: none;
  }
</style>
