<script lang="ts">
	import type { Breadcrumbs } from '$lib/client/types.gen.js';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import FileTable from '$lib/components/FileTable.svelte';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';

	let { data } = $props();

	let breadcrumbs = $derived(data.breadcrumbs as Breadcrumbs[]);
	let folders = $derived(data.folders);
	let files = $derived(data.files);
</script>

{#snippet children()}
	<Breadcrumb {breadcrumbs} />

	{#if folders?.length || files?.length}
		<FileTable bind:folders bind:files />
	{:else}
		<div class="flex h-full flex-col items-center justify-center gap-2 text-center">
			<span class="icon-[lucide--folder] size-32 text-muted-foreground"></span>

			<span class="text-lg font-medium">
				{m.empty_folder_title()}
			</span>

			<span class=" text-sm text-muted-foreground">
				{m.empty_folder_description()}
			</span>
		</div>
	{/if}
{/snippet}

<StorageLayout
	user={data.user}
	{children}
	folderId={data.folderId}
	availableSpace={data.availableSpace!}
/>
