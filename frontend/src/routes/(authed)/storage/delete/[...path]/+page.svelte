<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import { Input } from '$lib/components/ui/input';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import { formatBytes } from '$lib/utilities/storage';
	import { Search, Folder, File, House, EllipsisVertical, Trash2, History } from '@lucide/svelte';
	import DeleteAlertDialog from '$lib/components/DeleteAlertDialog.svelte';
	import type { FileFolderPublic } from '$lib/client/types.gen.js';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import StorageBreadcrumb from '$lib/components/StorageBreadcrumb.svelte';
	import StorageListButton from '$lib/components/StorageListButton.svelte';

	let { data } = $props();

	let segments = $derived(data.segments);
	let filteredItems = $state<FileFolderPublic[]>([]);

	let deleteDialogOpen = $state(false);

	$effect(() => {
		filteredItems = [...data.items];
	});
</script>

<div class="bg-tertiary-foreground flex h-full w-full">
	<main class="flex flex-1 flex-col gap-4 p-6">
		<div class="flex items-center justify-between">
			<div class="relative w-full max-w-124">
				<Search class="text-muted-foreground absolute top-1/2 left-4 size-5 -translate-y-1/2" />
				<Input type="text" class="w-full rounded-full pl-12" placeholder="Search..." />
			</div>
		</div>

		<div class="bg-background flex min-h-0 flex-1 flex-col rounded-lg p-4">
			<StorageBreadcrumb {segments} url="/storage/delete" />

			<div class="bg-background2 flex flex-row items-center justify-between rounded-lg px-2 py-4">
				<span class="text-muted-foreground text-sm"
					>Items in bin will be deleted forever after 30 days</span
				>
				<Button
					variant="ghost"
					class="border-primary text-primary hover:border-primary-high hover:text-primary-high cursor-pointer rounded-full border"
					>Empty Bin</Button
				>
			</div>

			<StorageSortHeader bind:filteredItems />

			<ScrollArea class="min-h-0 flex-1">
				{#each filteredItems as item, idx (idx)}
					{#if item.type === 'directory'}
						<StorageListButton mode='delete' {item} {segments} basePath='/storage/delete' />
					{:else}
						<StorageListButton mode='delete' {item} {segments} />
					{/if}
				{/each}
			</ScrollArea>
		</div>
	</main>
</div>

<DeleteAlertDialog bind:deleteDialogOpen />
