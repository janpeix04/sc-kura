<script lang="ts">
	import type { StorageSortKey } from "$lib/schemas/types";
	import { ChevronDown, ChevronUp } from "@lucide/svelte";
	import { Button } from "./ui/button";
	import type { FileFolderPublic } from "$lib/client";

    let { 
        filteredItems = $bindable(),
    }: {
        filteredItems: FileFolderPublic[];
    } = $props();

    let sortKey = $state<StorageSortKey>('name');
    let ascendant = $state<boolean>(false);
    let hasSorted = $state<boolean>(false);

    function sortItems(key: StorageSortKey) {
		if (!hasSorted) hasSorted = true;
		if (sortKey === key) ascendant = !ascendant;
		else {
			sortKey = key;
			ascendant = true;
		}

		filteredItems = [...filteredItems].sort((a, b) => {
			if (key === 'name')
				return ascendant ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name);
			if (key === 'size') return ascendant ? a.size - b.size : b.size - a.size;
			return ascendant
				? new Date(a.lastModified).getTime() - new Date(b.lastModified).getTime()
				: new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime();
		});
	}
</script>

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