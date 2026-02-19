<script lang="ts">
	import AppSidebar from '$lib/components/AppSidebar.svelte';
import UploadButton from '$lib/components/UploadButton.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import type { ComponentProps } from 'svelte';

    let {
        ref = $bindable(null),
        collapsible = "icon",
        ...restProps
    }: ComponentProps<typeof Sidebar.Root> = $props();
</script>

<div class="bg-tertiary-foreground flex h-full w-full">
    <AppSidebar/>
	<!-- <aside class="bg-tertiary-foreground flex h-full w-64 flex-col items-center gap-4 py-6">
		<UploadButton />
	</aside> -->

	<main class="flex flex-1 flex-col gap-4 overflow-auto p-6">
		<div class="flex flex-1 flex-col gap-4 rounded-lg bg-white p-4 shadow"></div>
	</main>
</div>
