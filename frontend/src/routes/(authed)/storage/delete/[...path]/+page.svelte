<script lang="ts">
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import Button from '$lib/components/ui/button/button.svelte';
	import { Input } from '$lib/components/ui/input';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import type { StorageSortKey } from '$lib/schemas/types';
	import { formatBytes } from '$lib/utilities/storage';
	import {
		Search,
		ChevronUp,
		ChevronDown,
		Folder,
		File,
		House,
		EllipsisVertical,
		Trash2,
		History
	} from '@lucide/svelte';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import DeleteAlertDialog from '$lib/components/DeleteAlertDialog.svelte';
	import type { FileFolderPublic } from '$lib/client/types.gen.js';

	let { data } = $props();

	let segments = $derived(data.segments);

	let sortKey: StorageSortKey = $state('name');
	let ascendant: boolean = $state(true);
	let hasSorted: boolean = $state(false);

	let deleteDialogOpen = $state(false);

	let filteredItems = $derived.by(() => {
		const items = [...data.items];

		if (!hasSorted) {
			return items;
		}

		return items.sort((a, b) => {
			if (sortKey === 'name')
				return ascendant ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name);

			if (sortKey === 'size') return ascendant ? a.size - b.size : b.size - a.size;

			return ascendant
				? new Date(a.lastModified).getTime() - new Date(b.lastModified).getTime()
				: new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime();
		});
	});

	function sortItems(key: StorageSortKey) {
		if (!hasSorted) hasSorted = true;
		if (sortKey === key) {
			ascendant = !ascendant;
		} else {
			sortKey = key;
			ascendant = true;
		}
	}
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
			<Breadcrumb.Root>
				<Breadcrumb.List class="mb-2 px-2">
					<Breadcrumb.Item>
						<Breadcrumb.Link href="/storage/delete"><House class="size-5" /></Breadcrumb.Link>
					</Breadcrumb.Item>
					{#each segments as folder, idx (idx)}
						<Breadcrumb.Separator />
						<Breadcrumb.Item>
							<Breadcrumb.Link href={`/storage/delete/${segments.slice(0, idx + 1).join('/')}`}>
								{folder}
							</Breadcrumb.Link>
						</Breadcrumb.Item>
					{/each}
				</Breadcrumb.List>
			</Breadcrumb.Root>
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
			<div class="flex shrink-0 items-center border-b">
				<Button
					class="flex flex-2 items-center justify-start gap-1"
					variant="ghost"
					onclick={() => sortItems('name')}
				>
					Name
					<span class="flex h-3 w-3 items-center justify-center">
						{#if sortKey === 'name' && hasSorted}
							{#if ascendant}<ChevronUp class="size-3" />{:else}<ChevronDown class="size-3" />{/if}
						{/if}
					</span>
				</Button>
				<Button
					class="flex w-50 items-center justify-start gap-1"
					variant="ghost"
					onclick={() => sortItems('size')}
				>
					Size
					<span class="flex h-3 w-3 items-center justify-center">
						{#if sortKey === 'size' && hasSorted}
							{#if ascendant}<ChevronUp class="size-3" />{:else}<ChevronDown class="size-3" />{/if}
						{/if}
					</span>
				</Button>
				<Button
					class="flex w-60 items-center justify-start gap-1"
					variant="ghost"
					onclick={() => sortItems('lastModified')}
				>
					Last modified
					<span class="flex h-3 w-3 items-center justify-center">
						{#if sortKey === 'lastModified' && hasSorted}
							{#if ascendant}<ChevronUp class="size-3" />{:else}<ChevronDown class="size-3" />{/if}
						{/if}
					</span>
				</Button>
			</div>

			<ScrollArea class="min-h-0 flex-1">
				{#each filteredItems as item, idx (idx)}
					{#if item.type === 'directory'}
						<div class="relative flex flex-row items-center">
							<Button
								variant="ghost"
								class="flex w-full flex-row items-center border-b py-5.5 text-sm"
								href={`/storage/delete/${[...segments, item.name].join('/')}`}
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
										<History class="size-4" />
										Restore
									</DropdownMenu.Item>
									<DropdownMenu.Item class="flex cursor-pointer items-center">
										<Trash2 class="size-4" />
										Delete forever
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
										<History class="size-4" />
										Restore
									</DropdownMenu.Item>
									<DropdownMenu.Item class="flex cursor-pointer items-center">
										<Trash2 class="size-4" />
										Delete forever
									</DropdownMenu.Item>
								</DropdownMenu.Content>
							</DropdownMenu.Root>
						</div>
					{/if}
				{/each}
			</ScrollArea>
		</div>
	</main>
</div>

<DeleteAlertDialog bind:deleteDialogOpen />
