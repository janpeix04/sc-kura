<script lang="ts">
	import { getContext, type Snippet } from 'svelte';
	import { cn } from '$lib/utils';

	type SidebarContext = {
		selected: () => string | null;
		select: (id: string) => void;
	};

	let {
		id,
		href,
		children,
		class: className,
		...rest
	}: {
		id: string;
		href?: string;
		children: Snippet;
		class?: string;
	} = $props();

	const sidebar = getContext<SidebarContext>('sidebar');
	const isActive = $derived(sidebar.selected() === id);

	function handleClick() {
		sidebar.select(id);
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
	<a {href} class="flex gap-4 items-center">
		{@render children()}
	</a>
</div>
