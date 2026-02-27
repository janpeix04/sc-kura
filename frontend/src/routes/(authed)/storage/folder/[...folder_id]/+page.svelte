<script lang="ts">
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import { toast } from 'svelte-sonner';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import StorageListButton from '$lib/components/StorageListButton.svelte';
	import { House } from '@lucide/svelte';
	import { storagePath } from '$lib/stores/storage.js';

	let { data, form } = $props();
	let items = $derived(data.items);

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
	$effect(() => {});
</script>

<div class="bg-tertiary-foreground flex h-full w-full">
	<main class="flex flex-1 flex-col gap-4 p-6">
		<div class="bg-background flex min-h-0 flex-1 flex-col rounded-lg p-4">
			<Breadcrumb.Root>
				<Breadcrumb.List class="mb-2 px-2">
					<Breadcrumb.Item>
						<Breadcrumb.Link href="/storage/my-files" onclick={() => storagePath.set([])}
							><House class="size-5" /></Breadcrumb.Link
						>
					</Breadcrumb.Item>
					{#each $storagePath as folder, idx (folder.id)}
						<Breadcrumb.Separator />
						<Breadcrumb.Item>
							<Breadcrumb.Link
								href={`/storage/folder/${folder.id}`}
								onclick={() => storagePath.update((path) => path.slice(0, idx + 1))}
							>
								{folder.name}
							</Breadcrumb.Link>
						</Breadcrumb.Item>
					{/each}
				</Breadcrumb.List>
			</Breadcrumb.Root>
			{#if items.length === 0}
				<div class="flex h-full flex-col items-center justify-center gap-2">
					<span class="icon-[ic--baseline-folder-copy] size-32 bg-amber-100"></span>
					<span class="text-xl font-semibold">Your folder is empty</span>
					<span>Use the Upload button to add files or Create to make a new folder</span>
				</div>
			{:else}
				<StorageSortHeader bind:filteredItems={items} />
				<ScrollArea class="min-h-0 flex-1">
					{#each items as item (item.id)}
						{#if item.type === 'directory'}
							<StorageListButton {item} basePath="/storage/folder" />
						{:else}
							<StorageListButton {item} />
						{/if}
					{/each}
				</ScrollArea>
			{/if}
		</div>
	</main>
</div>
