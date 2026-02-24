<script lang="ts">
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import Button from '$lib/components/ui/button/button.svelte';
	import { Input } from '$lib/components/ui/input';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import { STORAGE_LAYOUT } from '$lib/schemas/types';
	import { formatBytes } from '$lib/utilities/storage';
	import {
		Grid2x2,
		List,
		Search,
		Folder,
		File,
		House,
		EllipsisVertical,
		ArrowDownToLine,
		Trash2,
		PencilLine,
		Info
	} from '@lucide/svelte';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import { currentStoragePath } from '$lib/stores/storage.js';
	import {
		storageMoveToRecycleFileFileIdPost,
		storageMoveToRecycleFolderFolderIdPost
	} from '$lib/client/sdk.gen.js';
	import { createClient } from '$lib/client/client';
	import { toast } from 'svelte-sonner';
	import { storageItemsPathGet } from '$lib/client/sdk.gen.js';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import StorageBreadcrumb from '$lib/components/StorageBreadcrumb.svelte';
	import StorageListButton from '$lib/components/StorageListButton.svelte';
	import StorageMosaicButton from '$lib/components/StorageMosaicButton.svelte';

	let { data, form } = $props();

	const client = createClient({ baseUrl: '' });

	let segments = $derived(data.segments);
	let filteredItems = $derived(data.items);
	let folders = $derived(filteredItems.filter((item) => item.type === 'directory'));

	let layout: STORAGE_LAYOUT = $state(STORAGE_LAYOUT.List);

	function handleLayout() {
		switch (layout) {
			case STORAGE_LAYOUT.Grid2x2:
				layout = STORAGE_LAYOUT.List;
				break;
			default:
				layout = STORAGE_LAYOUT.Grid2x2;
				break;
		}
	}

	async function loadItems() {
		const { data: items } = await storageItemsPathGet({
			client,
			path: { path: $currentStoragePath },
			throwOnError: true
		});
		filteredItems = items;
	}

	async function moveFolderToRecycleBin(folderId: string) {
		const { data } = await storageMoveToRecycleFolderFolderIdPost({
			client,
			path: {
				folder_id: folderId
			},
			throwOnError: true
		});
		toast.success(data);
		await loadItems();
	}

	async function moveFileToRecycleBin(fileId: string) {
		const { data } = await storageMoveToRecycleFileFileIdPost({
			client,
			path: {
				file_id: fileId
			},
			throwOnError: true
		});
		toast.success(data);
		await loadItems();
	}

	$effect(() => {
		if (segments.length === 0) currentStoragePath.set('-');
		else currentStoragePath.set(segments.join('-'));
		loadItems().then(() => {});
	});

	$effect(() => {
		if (!form) return;

		if (form.uploadFilesError) {
			toast.error(form.uploadFilesError);
		}
		if (form.uploadFilesResult) {
			const result = form.uploadFilesResult;

			if (result.total_uploaded > 0) {
				toast.success(`Uploaded ${result.total_uploaded} file(s) successfully`);
			}

			if (result.total_errors > 0) {
				toast.error(`${result.total_errors} file(s) failed`, {
					description: result.errors.join('\n'),
					duration: 8000
				});
			}
		}
		if (form.createFolderError) {
			toast.error(form.createFolderError);
		}
		if (form.createFolderResult) {
			toast.success(form.createFolderResult);
		}
	});
</script>

<div class="bg-tertiary-foreground flex h-full w-full">
	<main class="flex flex-1 flex-col gap-4 p-6">
		<div class="flex items-center justify-between">
			<div class="relative w-full max-w-124">
				<Search class="text-muted-foreground absolute top-1/2 left-4 size-5 -translate-y-1/2" />
				<Input type="text" class="w-full rounded-full pl-12" placeholder="Search..." />
			</div>

			<Button variant="outline" onclick={handleLayout} class="ml-4 cursor-pointer">
				{#if layout === STORAGE_LAYOUT.Grid2x2}
					<Grid2x2 class="size-4.5" />
				{:else}
					<List class="size-4.5" />
				{/if}
			</Button>
		</div>

		<div class="bg-background flex min-h-0 flex-1 flex-col rounded-lg p-4">
			<StorageBreadcrumb {segments} basePath="/storage" />
			{#if layout === STORAGE_LAYOUT.List}
				<StorageSortHeader bind:filteredItems />

				<ScrollArea class="min-h-0 flex-1">
					{#each filteredItems as item, idx (idx)}
						{#if item.type === 'directory'}
							<StorageListButton
								{item}
								{segments}
								basePath="/storage"
								onRecycleBin={moveFolderToRecycleBin}
							/>
						{:else}
							<StorageListButton {item} {segments} onRecycleBin={moveFileToRecycleBin} />
						{/if}
					{/each}
				</ScrollArea>
			{:else}
				<ScrollArea class="min-h-0 flex-1">
					{#if folders.length > 0}
						<div class="mt-2 mb-10 flex flex-row flex-wrap gap-4">
							{#each folders as folder (folder.id)}
								<StorageMosaicButton {segments} item={folder} basePath="/storage" />
							{/each}
						</div>
					{/if}

					{#if filteredItems.length > 0}
						<div class="flex flex-row flex-wrap gap-4">
							{#each filteredItems as item (item.id)}
								{#if item.type !== 'directory'}
									<StorageMosaicButton {segments} {item} />
								{/if}
							{/each}
						</div>
					{/if}
				</ScrollArea>
			{/if}
		</div>
	</main>
</div>
