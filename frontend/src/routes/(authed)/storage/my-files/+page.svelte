<script>
	import { goto } from '$app/navigation';
	import StorageFolder from '$lib/components/StorageFolder.svelte';
	import StorageItemActions from '$lib/components/StorageItemActions.svelte';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import { formatBytes } from '$lib/utilities/storage.js';
	import { ChevronDown, ChevronRight, File } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';

	let { data, form } = $props();

	let items = $derived(data.items);

	$effect(() => {
		if (!form) return;

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
			<div class="py-2">
				<h2 class="font-semibold text-lg">My Files</h2>
			</div>
			<StorageSortHeader bind:filteredItems={items} />
			<ScrollArea class="min-h-0 flex-1">
				{#each items as item (item.id)}
					<Button variant="ghost" class="flex w-full flex-row items-center border-b py-5.5 text-sm">
						<div class="flex-2">
							<div class="flex flex-row items-center gap-2">
								{#if item.type === 'directory'}
									<span class="icon-[ic--baseline-folder] size-5 bg-gray-600"></span>
								{:else}
									<File class="size-5" />
								{/if}
								<span class="font-medium">{item.name}</span>
							</div>
						</div>
						<div class="text-muted-foreground flex w-50 items-center justify-start pl-10.5 text-sm">
							{formatBytes(item.size)}
						</div>
						<div
							class="text-muted-foreground flex w-60 items-center justify-between pl-8.5 text-sm"
						>
							{new Date(item.lastModified).toLocaleDateString('en-US', {
								month: 'short',
								day: 'numeric',
								year: 'numeric'
							})}
							<StorageItemActions item={item} />
						</div>
					</Button>
				{/each}
			</ScrollArea>
		</div>
	</main>
</div>
