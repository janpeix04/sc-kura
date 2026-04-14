<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		children,
        baseClass
	}: {
		children: Snippet;
        baseClass?: string;
	} = $props();
</script>

<div class="grid grid-cols-[7fr_1.5fr_1.5fr_1fr_0.2fr] {baseClass}">
	{@render children()}
</div>
