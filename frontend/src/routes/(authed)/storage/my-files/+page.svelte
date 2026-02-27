<script>
	import { goto } from '$app/navigation';
	import StorageListButton from '$lib/components/StorageListButton.svelte';
	import StorageSortHeader from '$lib/components/StorageSortHeader.svelte';
	import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
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
				<h2 class="text-lg font-semibold">My Files</h2>
			</div>
			{#if items.length === 0}
				<div class="flex h-full flex-col items-center justify-center gap-2">
					<span class="icon-[ic--baseline-folder-copy] size-32 bg-amber-100"></span>
					<span class="text-xl font-semibold">Your storage is empty</span>
					<span>Use the Upload button to add files or Create to make a new folder</span>
				</div>
			{:else}
				<StorageSortHeader bind:filteredItems={items} />
				<ScrollArea class="min-h-0 flex-1">
					{#each items as item (item.id)}
						<StorageListButton {item} />
					{/each}
				</ScrollArea>
			{/if}
		</div>
	</main>
</div>
