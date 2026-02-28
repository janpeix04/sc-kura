<script lang="ts">
	import type { FileFolderPublic } from '$lib/client';
	import { STORAGE_STATUS, type StorageMode } from '$lib/schemas/types';
	import { storagePath } from '$lib/stores/storage';
	import { formatBytes } from '$lib/utilities/storage';
	import StorageItemActions from './StorageItemActions.svelte';
	import { Button } from './ui/button';
	import { File } from '@lucide/svelte';

	let {
		item,
		basePath,
		mode = 'storage',
		status = STORAGE_STATUS.UPLOADED
	}: {
		item: FileFolderPublic;
		basePath? : string;
		mode?: StorageMode;
		status?: STORAGE_STATUS;
	} = $props();

	let href = $derived(basePath ? `${basePath}/${item.id}-${status}` : undefined);
</script>

<div class="relative flex w-full items-center justify-between">
	<Button 
		variant="ghost" 
		class="flex w-full flex-row items-center border-b py-5.5 text-sm" 
		{href}
		onclick={() => {
			if (href === undefined) return;
			storagePath.update((path) => [...path, item]);
		}}
	>
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
		<div class="text-muted-foreground flex w-60 items-center justify-between pl-8.5 text-sm">
			{new Date(item.lastModified).toLocaleDateString('en-US', {
				month: 'short',
				day: 'numeric',
				year: 'numeric'
			})}
		</div>
	</Button>
	<div class="absolute right-10 mt-1.5 items-center">
		<StorageItemActions {item} {mode} />
	</div>
</div>
