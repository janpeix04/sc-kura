<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import { Input } from '$lib/components/ui/input';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import { Search, Trash2 } from '@lucide/svelte';
	import DeleteAlertDialog from '$lib/components/DeleteAlertDialog.svelte';
	import type { FileFolderPublic } from '$lib/client/types.gen.js';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import StorageBreadcrumb from '$lib/components/StorageBreadcrumb.svelte';
	import StorageListButton from '$lib/components/StorageListButton.svelte';
	import { onMount } from 'svelte';
	import { deleteStorageFolderId } from '$lib/stores/storage.js';
	import {
		storageDeleteAllDelete,
		storageDeletedItemsGet,
	} from '$lib/client/sdk.gen.js';
	import { createClient } from '$lib/client/client/client.gen.js';
	import { get_path } from '$lib/utilities/storage.js';
	import { toast } from 'svelte-sonner';

	let { data } = $props();
	const client = createClient({ baseUrl: '' });
	let segments = $derived(data.segments);
	let filteredItems = $state<FileFolderPublic[]>([]);

	let deleteDialogOpen = $state(false);

	async function loadItems(folderId: string | undefined = undefined) {
		const { data: items } = await storageDeletedItemsGet({
			client,
			query: {
				folder_id: folderId
			},
			throwOnError: true
		});

		filteredItems = [...items];
	}

	async function emptyBin() {
		const { data } = await storageDeleteAllDelete({
			client,
			throwOnError: true
		});
		toast.success(data);
		deleteDialogOpen = false;
		await loadItems();
	}

	onMount(async () => {
		const path = get_path(segments);
		const folderId = $deleteStorageFolderId[path];
		await loadItems(folderId);
	});

	$effect(() => {
		const path = get_path(segments);
		const folderId = $deleteStorageFolderId[path];
		loadItems(folderId).then(() => {});
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
			<div class="font-medium mb-2">Recycle bin</div>
			{#if filteredItems.length === 0}
				<div class="flex h-full flex-col justify-center text-center items-center">
					<Trash2 class="size-54 stroke-1" />
					<span class="font-medium text-lg">The recycling bin is empty</span>
					<span class="text-sm"> Items moved to the recycle bin will be deleted forever after 30 days</span>
				</div>
			{:else}
				<StorageBreadcrumb {segments} basePath="/storage/delete" />
				{#if filteredItems.length > 0}
					<div
						class="bg-background2 flex flex-row items-center justify-between rounded-lg px-2 py-4"
					>
						<span class="text-muted-foreground text-sm"
							>Items in bin will be deleted forever after 30 days</span
						>
						<Button
							variant="ghost"
							class="border-primary text-primary hover:border-primary-high hover:text-primary-high cursor-pointer rounded-full border"
							onclick={() => {
								deleteDialogOpen = true;
							}}>Empty Bin</Button
						>
					</div>
				{/if}

				<StorageSortHeader bind:filteredItems />

				<ScrollArea class="min-h-0 flex-1">
					{#each filteredItems as item, idx (idx)}
						{#if item.type === 'directory'}
							<StorageListButton
								mode="delete"
								{item}
								{segments}
								basePath="/storage/delete"
								onClick={async () => {
									const path = item.path;
									const folder = filteredItems.find(
										(f) => f.type === 'directory' && f.path === path
									);
									if (folder) {
										if (!$deleteStorageFolderId[path]) {
											deleteStorageFolderId.update((prev) => ({
												...prev,
												[folder.path]: folder.id
											}));
										}
									}
								}}
							/>
						{:else}
							<StorageListButton mode="delete" {item} {segments} />
						{/if}
					{/each}
				</ScrollArea>
			{/if}
		</div>
	</main>
</div>

<DeleteAlertDialog bind:deleteDialogOpen onClick={() => emptyBin()} />
