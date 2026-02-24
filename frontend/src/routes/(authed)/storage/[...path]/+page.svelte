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

	async function movFolderToRecycleBin(folderId: string) {
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
			<Breadcrumb.Root>
				<Breadcrumb.List class="mb-2 px-2">
					<Breadcrumb.Item>
						<Breadcrumb.Link href="/storage"><House class="size-5" /></Breadcrumb.Link>
					</Breadcrumb.Item>
					{#each segments as folder, idx (idx)}
						<Breadcrumb.Separator />
						<Breadcrumb.Item>
							<Breadcrumb.Link href={`/storage/${segments.slice(0, idx + 1).join('/')}`}>
								{folder}
							</Breadcrumb.Link>
						</Breadcrumb.Item>
					{/each}
				</Breadcrumb.List>
			</Breadcrumb.Root>
			{#if layout === STORAGE_LAYOUT.List}
				<StorageSortHeader bind:filteredItems />

				<ScrollArea class="min-h-0 flex-1">
					{#each filteredItems as item, idx (idx)}
						{#if item.type === 'directory'}
							<div class="relative flex flex-row items-center">
								<Button
									variant="ghost"
									class="flex w-full flex-row items-center border-b py-5.5 text-sm"
									href={`/storage/${[...segments, item.name].join('/')}`}
								>
									<div class="flex-2">
										<div class="flex flex-row items-center gap-2">
											{#if item.type === 'directory'}
												<Folder class="size-5" />
											{:else}
												<File class="size-5" />
											{/if}
											<span class="font-medium">{item.name}</span>
										</div>
									</div>
									<div
										class="text-muted-foreground flex w-50 items-center justify-start pl-10.5 text-sm"
									>
										{formatBytes(item.size)}
									</div>
									<div
										class="text-muted-foreground flex w-60 items-center justify-start pl-8.5 text-sm"
									>
										{new Date(item.lastModified).toLocaleDateString('en-US', {
											month: 'short',
											day: 'numeric',
											year: 'numeric'
										})}
									</div>
								</Button>
								<DropdownMenu.Root>
									<DropdownMenu.Trigger class="absolute right-5 cursor-pointer">
										<EllipsisVertical class="size-5" />
									</DropdownMenu.Trigger>
									<DropdownMenu.Content align="end">
										<DropdownMenu.Item class="flex cursor-pointer items-center">
											<ArrowDownToLine class="size-4" />
											Download
										</DropdownMenu.Item>
										<DropdownMenu.Item class="flex cursor-pointer items-center">
											<PencilLine class="size-4" />
											Rename
										</DropdownMenu.Item>
										<DropdownMenu.Separator />
										<DropdownMenu.Item class="flex cursor-pointer items-center">
											<Info class="size-4" />
											Folder information
										</DropdownMenu.Item>
										<DropdownMenu.Separator />
										<DropdownMenu.Item
											class="flex cursor-pointer items-center"
											onclick={async () => await moveFileToRecycleBin(item.id)}
										>
											<Trash2 class="size-4" />
											Delete
										</DropdownMenu.Item>
									</DropdownMenu.Content>
								</DropdownMenu.Root>
							</div>
						{:else}
							<div class="relative flex flex-row items-center">
								<Button
									variant="ghost"
									class="flex w-full flex-row items-center border-b py-5.5 text-sm"
								>
									<div class="flex-2">
										<div class="flex flex-row items-center gap-2">
											{#if item.type === 'directory'}
												<Folder class="size-5" />
											{:else}
												<File class="size-5" />
											{/if}
											<span class="font-medium">{item.name}</span>
										</div>
									</div>
									<div
										class="text-muted-foreground flex w-50 items-center justify-start pl-10.5 text-sm"
									>
										{formatBytes(item.size)}
									</div>
									<div
										class="text-muted-foreground flex w-60 items-center justify-start pl-8.5 text-sm"
									>
										{new Date(item.lastModified).toLocaleDateString('en-US', {
											month: 'short',
											day: 'numeric',
											year: 'numeric'
										})}
									</div>
								</Button>
								<DropdownMenu.Root>
									<DropdownMenu.Trigger class="absolute right-5 cursor-pointer">
										<EllipsisVertical class="size-5" />
									</DropdownMenu.Trigger>
									<DropdownMenu.Content align="end">
										<DropdownMenu.Item class="flex cursor-pointer items-center">
											<ArrowDownToLine class="size-4" />
											Download
										</DropdownMenu.Item>
										<DropdownMenu.Item class="flex cursor-pointer items-center">
											<PencilLine class="size-4" />
											Rename
										</DropdownMenu.Item>
										<DropdownMenu.Separator />
										<DropdownMenu.Item class="flex cursor-pointer items-center">
											<Info class="size-4" />
											Folder information
										</DropdownMenu.Item>
										<DropdownMenu.Separator />
										<DropdownMenu.Item
											class="flex cursor-pointer items-center"
											onclick={async () => await moveFileToRecycleBin(item.id)}
										>
											<Trash2 class="size-4" />
											Delete
										</DropdownMenu.Item>
									</DropdownMenu.Content>
								</DropdownMenu.Root>
							</div>
						{/if}
					{/each}
				</ScrollArea>
			{:else}
				<ScrollArea class="min-h-0 flex-1">
					<div class="mt-2 mb-10 flex flex-row flex-wrap gap-4">
						{#each folders as folder, idx (idx)}
							<Button
								variant="outline"
								class="bg-background2 flex w-64 flex-row items-center justify-start py-5"
								href={`/storage/${[...segments, folder.name].join('/')}`}
							>
								<Folder class="size-5 shrink-0" />
								<span class="flex-1 truncate text-left font-medium">{folder.name}</span>
							</Button>
						{/each}
					</div>
					<div class="flex flex-row flex-wrap gap-4">
						{#each filteredItems as item, idx (idx)}
							{#if item.type !== 'directory'}
								<Button
									variant="ghost"
									class="bg-background2 flex h-48 w-48 flex-col overflow-hidden rounded-lg pb-4 shadow sm:h-56 sm:w-56 md:h-64 md:w-64"
								>
									<div class="flex gap-4 self-start p-2">
										{#if item.type === 'directory'}
											<Folder class="size-5 shrink-0" />
										{:else}
											<File class="size-5 shrink-0" />
										{/if}
										<span class="flex-1 truncate text-left font-medium">{item.name}</span>
									</div>

									<div class="flex w-full flex-1 items-center justify-center rounded-lg bg-white">
										<span class="text-sm text-gray-400">Preview</span>
									</div>
								</Button>
							{/if}
						{/each}
					</div>
				</ScrollArea>
			{/if}
		</div>
	</main>
</div>
