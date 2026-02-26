<script>
	import StorageFolder from '$lib/components/StorageFolder.svelte';
	import StorageItemActions from '$lib/components/StorageItemActions.svelte';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import { formatBytes } from '$lib/utilities/storage.js';
	import { ChevronDown, ChevronRight, File } from '@lucide/svelte';

	let { data } = $props();

	let suggestedFolders = $derived(data.suggestedFolders);
	let suggestedFiles = $derived(data.suggestedFiles);

	let isFolderCollapsibleOpen = $state(true);
	let isFileCollapsibleOpen = $state(true);
</script>

<div class="bg-tertiary-foreground flex h-full w-full">
	<main class="flex flex-1 flex-col gap-4 p-6">
		<div class="bg-background flex min-h-0 flex-1 flex-col rounded-lg p-4">
			<div class="mt-4 text-center text-2xl font-medium">Welcome to Kura</div>

			<Collapsible.Root bind:open={isFolderCollapsibleOpen}>
				<Collapsible.Trigger
					class="hover:bg-sidebar-accent flex cursor-pointer flex-row items-center gap-1 rounded-full px-2 py-1"
				>
					{#if isFolderCollapsibleOpen}
						<ChevronDown class="size-5.5" />
					{:else}
						<ChevronRight class="size-5.5" />
					{/if}
					<span class="font-medium">Suggested folders</span>
				</Collapsible.Trigger>
				<Collapsible.Content>
					<ScrollArea>
						<div class="mt-2 mb-10 flex flex-row flex-wrap gap-4">
							{#each suggestedFolders as folder (folder.id)}
								<StorageFolder {folder} />
							{/each}
						</div>
					</ScrollArea>
				</Collapsible.Content>
			</Collapsible.Root>

			<Collapsible.Root bind:open={isFileCollapsibleOpen} class="flex flex-col min-h-0 flex-1">
				<Collapsible.Trigger
					class="hover:bg-sidebar-accent mt-6 flex cursor-pointer flex-row items-center gap-1 rounded-full px-2 py-1"
				>
					{#if isFileCollapsibleOpen}
						<ChevronDown class="size-5.5" />
					{:else}
						<ChevronRight class="size-5.5" />
					{/if}
					<span class="font-medium">Suggested files</span>
				</Collapsible.Trigger>
				<Collapsible.Content class="flex flex-col min-h-0">
					<StorageSortHeader bind:filteredItems={suggestedFiles} />
					<ScrollArea class="min-h-0 flex-1">
						{#each suggestedFiles as file (file.id)}
							<Button
								variant="ghost"
								class="flex w-full flex-row items-center border-b py-5.5 text-sm"
							>
								<div class="flex-2">
									<div class="flex flex-row items-center gap-2">
										<File class="size-5" />
										<span class="font-medium">{file.name}</span>
									</div>
								</div>
								<div
									class="text-muted-foreground flex w-50 items-center justify-start pl-10.5 text-sm"
								>
									{formatBytes(file.size)}
								</div>
								<div
									class="text-muted-foreground flex w-60 items-center justify-between pl-8.5 text-sm"
								>
									{new Date(file.lastModified).toLocaleDateString('en-US', {
										month: 'short',
										day: 'numeric',
										year: 'numeric'
									})}
									<StorageItemActions item={file} />
								</div>
							</Button>
						{/each}
					</ScrollArea>
				</Collapsible.Content>
			</Collapsible.Root>
		</div>
	</main>
</div>
