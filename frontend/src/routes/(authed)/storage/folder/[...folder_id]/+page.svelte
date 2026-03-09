<script lang="ts">
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import { toast } from 'svelte-sonner';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import StorageListButton from '$lib/components/StorageListButton.svelte';
	import { House } from '@lucide/svelte';
	import { storagePath } from '$lib/stores/storage.js';
	import { STORAGE_STATUS } from '$lib/schemas/types.js';
	import { updateStorageAvailableSpace } from '$lib/utilities/storage.js';

	let { data, form } = $props();
	let folders = $derived(data.folders);
	let files = $derived(data.files);
	let status = $derived(data.status as STORAGE_STATUS);

	$effect(() => {
		if (!form) return;

		if (form.uploadFilesError) {
			toast.error(form.uploadFilesError);
		}
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
		}
		if (form.createFolderError) {
			toast.error(form.createFolderError);
		}
		if (form.createFolderResult) {
			toast.success(form.createFolderResult);
		}
	});
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
								href={`/storage/folder/${folder.id}-${status}`}
								onclick={() => storagePath.update((path) => path.slice(0, idx + 1))}
							>
								{folder.name}
							</Breadcrumb.Link>
						</Breadcrumb.Item>
					{/each}
				</Breadcrumb.List>
			</Breadcrumb.Root>
			{#if folders.length === 0 && files.length === 0}
				<div class="flex h-full flex-col items-center justify-center gap-2">
					<span class="icon-[ic--baseline-folder-copy] size-32 bg-amber-100"></span>
					<span class="text-xl font-semibold">Your folder is empty</span>
					<span>Use the Upload button to add files or Create to make a new folder</span>
				</div>
			{:else}
				<StorageSortHeader bind:filteredFolders={folders} bind:filteredFiles={files} />
				<ScrollArea class="min-h-0 flex-1">
					{#each folders as folder (folder.id)}
						<StorageListButton
								item={folder}
								basePath="/storage/folder"
								{status}
								mode={status === STORAGE_STATUS.DELETED ? 'delete' : 'storage'}
							/>
					{/each}
					{#each files as file (file.id)}
						<StorageListButton
							item={file}
							{status}
							mode={status === STORAGE_STATUS.DELETED ? 'delete' : 'storage'}
						/>
					{/each}
				</ScrollArea>
			{/if}
		</div>
	</main>
</div>
