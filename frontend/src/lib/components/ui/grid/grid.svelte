<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		children
	}: {
		children: Snippet;
	} = $props();
</script>

<div class="grid grid-cols-[7fr_1.5fr_1.5fr_1fr_0.2fr]">
	{@render children()}
</div>
