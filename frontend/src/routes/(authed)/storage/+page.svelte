<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import { Input } from '$lib/components/ui/input';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import { STORAGE_LAYOUT, type StorageSortKey } from '$lib/schemas/types';
	import { formatBytes } from '$lib/utilities/storage';
	import {
		Grid2x2,
		Grid3x2,
		List,
		Search,
		ChevronUp,
		ChevronDown,
		Folder,
		File
	} from '@lucide/svelte';

	let { data } = $props();

	let items = $derived(data.items);
	let filteredItems = $state([...items]);

	let layout: STORAGE_LAYOUT = $state(STORAGE_LAYOUT.Grid2x2);
	let sortKey: StorageSortKey = $state('name');
	let ascendant: boolean = $state(true);
	let hasSorted: boolean = $state(false);

	function handleLayout() {
		switch (layout) {
			case STORAGE_LAYOUT.Grid3x2:
				layout = STORAGE_LAYOUT.Grid2x2;
				break;
			case STORAGE_LAYOUT.Grid2x2:
				layout = STORAGE_LAYOUT.List;
				break;
			default:
				layout = STORAGE_LAYOUT.Grid3x2;
				break;
		}
	}

	function sortItems(key: StorageSortKey) {
		if (!hasSorted) hasSorted = true;
		if (sortKey === key) ascendant = !ascendant;
		else {
			sortKey = key;
			ascendant = true;
		}

		filteredItems = [...items].sort((a, b) => {
			if (key === 'name')
				return ascendant ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name);
			if (key === 'size') return ascendant ? a.size - b.size : b.size - a.size;
			return ascendant
				? a.lastModified.getTime() - b.lastModified.getTime()
				: b.lastModified.getTime() - a.lastModified.getTime();
		});
	}
</script>

<div class="bg-tertiary-foreground flex h-full w-full">
	<main class="flex flex-1 flex-col gap-4 p-6">
		<div class="flex items-center justify-between">
			<div class="relative w-full max-w-124">
				<Search class="text-muted-foreground absolute top-1/2 left-4 size-5 -translate-y-1/2" />
				<Input type="text" class="w-full rounded-full pl-12" placeholder="Search..." />
			</div>

			<Button variant="outline" onclick={handleLayout} class="ml-4 cursor-pointer">
				{#if layout === STORAGE_LAYOUT.Grid3x2}
					<Grid3x2 class="size-4.5" />
				{:else if layout === STORAGE_LAYOUT.Grid2x2}
					<Grid2x2 class="size-4.5" />
				{:else}
					<List class="size-4.5" />
				{/if}
			</Button>
		</div>

		<div class="bg-background flex min-h-0 flex-1 flex-col rounded-lg p-4">
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
			{#if layout === STORAGE_LAYOUT.List}
				<ScrollArea class="min-h-0 flex-1">
					{#each filteredItems as item, idx (idx)}
						<Button
							variant="ghost"
							class="flex w-full flex-row items-center border-b py-5.5 text-base"
						>
							<div class="flex-2">
								<div class="flex flex-row items-center gap-2">
									{#if item.type === 'directory'}
										<Folder class="size-5" />
									{:else}
										<File class="size-5" />
									{/if}
									<span>{item.name}</span>
								</div>
							</div>
							<div class="text-muted-foreground w-28 pl-1 text-sm">{formatBytes(item.size)}</div>
							<div class="text-muted-foreground w-80 pl-1 text-sm">
								{item.lastModified.toLocaleDateString('en-US', {
									month: 'short',
									day: 'numeric',
									year: 'numeric'
								})}
							</div>
						</Button>
					{/each}
				</ScrollArea>
			{:else if layout === STORAGE_LAYOUT.Grid3x2}
				<ScrollArea class="min-h-0 flex-1">
					<div class="mt-4 flex flex-row flex-wrap gap-4">
						{#each filteredItems as item, idx (idx)}
							<Button
								variant="ghost"
								class="flex h-18 w-64 shrink-0 items-center justify-start border shadow"
							>
								{#if item.type === 'directory'}
									<Folder class="size-14" />
								{:else}
									<File class="size-14" />
								{/if}

								<div class="flex flex-col text-left">
									<span>{item.name}</span>
									<span class="text-muted-foreground text-sm">{formatBytes(item.size)}</span>
									<span class="text-muted-foreground text-sm">
										{item.lastModified.toLocaleDateString('en-US', {
											month: 'short',
											day: 'numeric',
											year: 'numeric'
										})}
									</span>
								</div>
							</Button>
						{/each}
					</div>
				</ScrollArea>
			{:else}
				<ScrollArea class="min-h-0 min-w-0 flex-1">
					<div class="mt-4 flex flex-row flex-wrap gap-4">
						{#each filteredItems as item, idx (idx)}
							<Button
								variant="ghost"
								class="flex h-48 w-48 flex-col overflow-hidden rounded-lg bg-primary px-2 pb-2 shadow sm:h-56 sm:w-56 md:h-64 md:w-64"
							>
								<div class="flex flex-row items-center gap-2 p-2">
									{#if item.type === 'directory'}
										<Folder class="size-5 shrink-0" />
									{:else}
										<File class="size-5 shrink-0" />
									{/if}
									<span class="flex-1 truncate text-left font-medium">{item.name}</span>
								</div>

								<div class="flex w-full flex-1 items-center justify-center rounded-lg bg-white p-2">
									<span class="text-sm text-gray-400">Preview</span>
								</div>
							</Button>
						{/each}
					</div>
				</ScrollArea>
				<!-- <ScrollArea class="min-h-0 min-w-0 flex-1">
					<div class="flex flex-wrap gap-4 p-2">
						{#each filteredItems as item (item.name)}
							<div
								class="flex aspect-square w-48 flex-col overflow-hidden rounded-lg bg-gray-100 shadow sm:w-56 md:w-64 px-2 pb-2"
							>
								<div class="flex flex-row items-center gap-2 p-2">
									{#if item.type === 'directory'}
										<Folder class="size-5 shrink-0" />
									{:else}
										<File class="size-5 shrink-0" />
									{/if}
									<span class="truncate font-medium">{item.name}</span>
								</div>

								<div class="flex w-full flex-1 items-center justify-center bg-white p-2 rounded-lg">
									<span class="text-sm text-gray-400">Preview</span>
								</div>
							</div>
						{/each}
					</div>
				</ScrollArea> -->
			{/if}
		</div>
	</main>
</div>
