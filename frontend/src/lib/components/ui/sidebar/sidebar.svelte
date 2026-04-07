<script lang="ts">
	import { setContext, type Snippet } from 'svelte';

	type SidebarContext = {
		selected: () => string | null;
		select: (id: string) => void;
	};

	const {
		initial = null,
		children
	}: {
		initial?: string | null;
		children: Snippet;
	} = $props();

	let selected = $state<string | null>(initial);

	function select(id: string) {
		selected = id;
	}

	setContext<SidebarContext>('sidebar', {
		selected: () => selected,
		select
	});
</script>

<div class="group mt-6 flex w-full flex-col gap-2">
	{@render children()}
</div>
