<script lang="ts">
  import { onMount } from "svelte";

  export let target: string | HTMLElement = "body";

  let node: HTMLDivElement;

  onMount(() => {
    const dest =
      typeof target === "string"
        ? document.querySelector(target) ?? document.body
        : target;
    dest.appendChild(node);
    return () => {
      node.remove();
    };
  });
</script>

<div bind:this={node} style="display: contents">
  <slot />
</div>
