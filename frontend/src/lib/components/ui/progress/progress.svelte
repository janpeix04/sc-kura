<script lang="ts">
	import { cn } from '$lib/utils';
	import type { HTMLAttributes } from 'svelte/elements';

	interface Props extends HTMLAttributes<HTMLDivElement> {
		ref?: HTMLDivElement | null;
		class?: string;
		value?: number;
		max?: number;
	}

	let {
		ref = $bindable(null),
		class: className,
		value = 0,
		max = 100,
		...restProps
	}: Props = $props();

	const percentage = $derived(Math.max(0, Math.min(100, (100 * value) / Math.max(max, 1))));
</script>

<div
	bind:this={ref}
	data-slot="progress"
	role="progressbar"
	aria-valuemin={0}
	aria-valuemax={max}
	aria-valuenow={value}
	class={cn(
		'relative flex h-1.5 w-full items-center overflow-x-hidden rounded-full bg-muted',
		className
	)}
	{...restProps}
>
	<div
		data-slot="progress-indicator"
		class="h-full bg-primary transition-all"
		style={`width: ${percentage}%`}
	></div>
</div>
