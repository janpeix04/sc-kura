<script lang="ts">
	import type { Snippet } from 'svelte';

	const {
		children
	}: {
		children: Snippet;
	} = $props();
</script>

<div class="group mt-6 flex w-full flex-col gap-2">
	{@render children()}
</div>
