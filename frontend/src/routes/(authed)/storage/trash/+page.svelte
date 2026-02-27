<script lang="ts">
	import StorageListButton from '$lib/components/StorageListButton.svelte';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import { ScrollArea } from '$lib/components/ui/scroll-area';

	let { data } = $props();

	let items = $derived(data.items);

	$effect(() => {
		console.log('Items:', items);
	});
</script>

<div class="bg-tertiary-foreground flex h-full w-full">
	<main class="flex flex-1 flex-col gap-4 p-6">
		<div class="bg-background flex min-h-0 flex-1 flex-col rounded-lg p-4">
			<div class="py-2">
				<h2 class="text-lg font-semibold">Trash</h2>
			</div>

			{#if items.length === 0}
				<div class="flex h-full flex-col items-center justify-center gap-2">
					<span class="icon-[mdi--trash-can-empty] size-32 bg-gray-300"></span>
					<span class="text-xl font-semibold">Trash is empty</span>
					<span>Items moved to the recycle bin will be deleted forever after 30 days</span>
				</div>
			{:else}
				<StorageSortHeader bind:filteredItems={items} />
				<ScrollArea class="min-h-0 flex-1">
					{#each items as item (item.id)}
						{#if item.type === 'directory'}
							<StorageListButton {item} basePath="/storage/folder" mode="delete" />
						{:else}
							<StorageListButton {item} mode="delete" />
						{/if}
					{/each}
				</ScrollArea>
			{/if}
		</div>
	</main>
</div>
