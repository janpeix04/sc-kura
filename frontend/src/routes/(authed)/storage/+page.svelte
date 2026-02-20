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

	let layout: STORAGE_LAYOUT = $state(STORAGE_LAYOUT.Grid3x2);
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

		<div class="bg-background flex flex-1 flex-col rounded-lg p-4 min-h-0">
			<div class="flex items-center border-b shrink-0">
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
					class="flex w-32 items-center justify-start gap-1"
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
					class="flex w-40 items-center justify-start gap-1"
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
			<ScrollArea class="flex-1 min-h-0">
				{#each filteredItems as item, idx (idx)}
					<Button variant='ghost' class="w-full flex flex-row items-center text-base py-5.5 border-b">
						<div class="flex-2">
                            <div class="flex flex-row gap-2 items-center">
                                {#if item.type === 'directory'}
                                <Folder class="size-5" />
                            {:else}
                                <File class="size-5" />
                            {/if}
                            <span>{item.name}</span>
                            </div>
                        </div>
						<div class="w-32 pl-1 text-sm text-muted-foreground">{formatBytes(item.size)}</div>
						<div class="w-40 pl-1 text-sm text-muted-foreground">
							{item.lastModified.toLocaleDateString('en-US', {
								month: 'short',
								day: 'numeric',
								year: 'numeric'
							})}
						</div>
					</Button>
				{/each}
			</ScrollArea>
		</div>
	</main>
</div>
