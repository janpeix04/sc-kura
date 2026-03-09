<script>
	import { goto } from '$app/navigation';
	import StorageFolder from '$lib/components/StorageFolder.svelte';
	import StorageListButton from '$lib/components/StorageListButton.svelte';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import { updateStorageAvailableSpace } from '$lib/utilities/storage.js';
	import { ChevronDown, ChevronRight } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';

	let { data, form } = $props();

	let suggestedFolders = $derived(data.suggestedFolders);
	let suggestedFiles = $derived(data.suggestedFiles);

	let isFolderCollapsibleOpen = $state(true);
	let isFileCollapsibleOpen = $state(true);

	$effect(() => {
		if (!form) return;

		if (form.uploadFilesResult) {
			updateStorageAvailableSpace();
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
			goto('/storage/my-files');
		}

		if (form.uploadFilesError) {
			toast.error(form.uploadFilesError);
			goto('/storage/my-files');
		}

		if (form.createFolderResult) {
			toast.success(form.createFolderResult);
			goto('/storage/my-files');
		}

		if (form.createFolderError) {
			toast.error(form.createFolderError);
			goto('/storage/my-files');
		}
	});
</script>

<div class="bg-tertiary-foreground flex h-full w-full">
	<main class="flex flex-1 flex-col gap-4 p-6">
		<div class="bg-background flex min-h-0 flex-1 flex-col rounded-lg p-4">
			<div class="mt-4 text-center text-2xl font-medium">Welcome to Kura</div>

			<Collapsible.Root bind:open={isFolderCollapsibleOpen} class="mb-2">
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
						<div class="mt-2 flex flex-row flex-wrap gap-4">
							{#each suggestedFolders as folder (folder.id)}
								<StorageFolder {folder} />
							{/each}
						</div>
					</ScrollArea>
				</Collapsible.Content>
			</Collapsible.Root>

			<Collapsible.Root bind:open={isFileCollapsibleOpen} class="flex min-h-0 flex-1 flex-col">
				<Collapsible.Trigger
					class="hover:bg-sidebar-accent flex cursor-pointer flex-row items-center gap-1 rounded-full px-2 py-1"
				>
					{#if isFileCollapsibleOpen}
						<ChevronDown class="size-5.5" />
					{:else}
						<ChevronRight class="size-5.5" />
					{/if}
					<span class="font-medium">Suggested files</span>
				</Collapsible.Trigger>
				<Collapsible.Content class="flex min-h-0 flex-col">
					{#if suggestedFiles.length > 0}
						<StorageSortHeader
							bind:filteredFolders={suggestedFolders}
							bind:filteredFiles={suggestedFiles}
						/>
						<ScrollArea class="min-h-0 flex-1">
							{#each suggestedFiles as file (file.id)}
								<StorageListButton item={file} />
							{/each}
						</ScrollArea>
					{/if}
				</Collapsible.Content>
			</Collapsible.Root>
		</div>
	</main>
</div>
