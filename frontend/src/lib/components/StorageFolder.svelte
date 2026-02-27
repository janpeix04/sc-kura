<script lang="ts">
	import type { FileFolderPublic } from '$lib/client';
	import { storagePath } from '$lib/stores/storage';
	import StorageItemActions from './StorageItemActions.svelte';
	import { Button } from './ui/button';

	let {
		folder
	}: {
		folder: FileFolderPublic;
	} = $props();
</script>

<Button
	variant="outline"
	class="bg-background2 flex w-64 flex-row items-center justify-start py-5"
	href={`/storage/folder/${folder.id}`}
	onclick={() => {
		storagePath.update((path) => [...path, folder]);
	}}
>
	<span class="icon-[ic--baseline-folder] size-5 bg-gray-600"></span>
	<span class="flex-1 truncate text-left font-medium">{folder.name}</span>

	<StorageItemActions item={folder} />
</Button>
