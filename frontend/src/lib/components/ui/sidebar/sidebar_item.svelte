<script lang="ts">
	import type { Snippet } from 'svelte';
	import { cn } from '$lib/utils';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';

	let {
		href,
		children,
		class: className,
		...rest
	}: {
		href: string;
		children: Snippet;
		class?: string;
	} = $props();

	const isActive = $derived(page.url.pathname === href);

	function handleClick() {
		goto(href);
	}

	const classes = $derived(
		cn(
			'flex items-center gap-4 px-4 py-1 rounded-full cursor-pointer',
			isActive && 'bg-selected text-on-selected',
			!isActive && 'hover:bg-hover',
			className
		)
	);
</script>

<div onclick={handleClick} class={classes} {...rest}>
	{@render children()}
</div>
