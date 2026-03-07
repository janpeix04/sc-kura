<script lang="ts">
	import { goto } from '$app/navigation';
	import EmptyTrashDialog from '$lib/components/EmptyTrashDialog.svelte';
	import StorageListButton from '$lib/components/StorageListButton.svelte';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import { STORAGE_STATUS } from '$lib/schemas/types.js';
	import { toast } from 'svelte-sonner';

	let { data, form } = $props();

	let folders = $derived(data.folders ?? []);
	let files = $derived(data.files ?? []);
	let deleteDialogOpen = $state(false);

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
				<h2 class="text-lg font-semibold">Trash</h2>
			</div>

			{#if folders.length === 0 && files.length === 0}
				<div class="flex h-full flex-col items-center justify-center gap-2">
					<span class="icon-[mdi--trash-can-empty] size-32 bg-gray-300"></span>
					<span class="text-xl font-semibold">Trash is empty</span>
					<span>Items moved to the recycle bin will be deleted forever after 30 days</span>
				</div>
			{:else}
				<div class="bg-background2 flex flex-row items-center justify-between rounded-lg px-2 py-4">
					<span class="text-muted-foreground text-sm"
						>Items in trash will be deleted forever after 30 days</span
					>
					<Button
						variant="ghost"
						class="border-primary text-primary hover:border-primary-high hover:text-primary-high cursor-pointer rounded-full border"
						onclick={() => {
							deleteDialogOpen = true;
						}}>Empty Trash</Button
					>
				</div>
				<StorageSortHeader bind:filteredFolders={folders} bind:filteredFiles={files} />
				<ScrollArea class="min-h-0 flex-1">
					{#each folders as folder (folder.id)}
						<StorageListButton
							item={folder}
							basePath="/storage/folder"
							mode="delete"
							status={STORAGE_STATUS.DELETED}
						/>
					{/each}
					{#each files as file (file.id)}
						<StorageListButton item={file} mode="delete" />
					{/each}
				</ScrollArea>
			{/if}
		</div>
	</main>
</div>

<EmptyTrashDialog bind:open={deleteDialogOpen} />
