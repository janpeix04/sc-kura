<script>
	import StorageFolder from '$lib/components/StorageFolder.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import { ChevronDown, ChevronRight } from '@lucide/svelte';

	let { data } = $props();

	let suggestedFolders = $derived(data.suggestedFolders);

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
							{#each suggestedFolders as folder, idx (idx)}
								<StorageFolder {folder} />
							{/each}
						</div>
					</ScrollArea>
				</Collapsible.Content>
			</Collapsible.Root>

			<Collapsible.Root bind:open={isFileCollapsibleOpen}>
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
				<Collapsible.Content>tewewr rwerew rwerewewrwe rwe</Collapsible.Content>
			</Collapsible.Root>
		</div>
	</main>
</div>
