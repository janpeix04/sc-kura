<script lang="ts">
	import { cn } from '$lib/utils';
	import type { Snippet } from 'svelte';

	let {
		spaced = false,
		children,
		class: className,
		...rest
	}: {
		spaced?: boolean;
		children: Snippet;
		class?: string;
	} = $props();

	const classes = $derived(() => cn('flex flex-col gap-2', spaced && 'mt-5', className));
</script>

<div class={classes()} {...rest}>
	{@render children()}
</div>
