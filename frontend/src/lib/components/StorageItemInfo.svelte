<script lang="ts">
	import type { FilePublic, FolderPublic } from '$lib/client';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { formatBytes } from '$lib/utilities/storage';
	import { File } from '@lucide/svelte';

	let { 
		open = $bindable(), 
		item 
	}: { 
		open: boolean; 
		item: FolderPublic |FilePublic 
	} = $props();

	const formattedDate = $derived(new Date(item.lastModified).toLocaleDateString('en-US', {
		month: 'long',
		day: 'numeric',
		year: 'numeric'
	}));
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="w-105">
		<Dialog.Header class="space-y-3">
			<div class="flex items-center gap-3">
				<div class="bg-muted flex size-10 items-center justify-center rounded-lg">
					{#if item.type === 'directory'}
						<span class="icon-[ic--baseline-folder] size-5 bg-gray-600"></span>
					{:else}
						<File class="size-5 text-foreground" />
					{/if}
				</div>
				<div>
					<Dialog.Title class="text-lg font-semibold">
						{item.name}
					</Dialog.Title>
					<p class="text-muted-foreground text-sm">
						{item.type === 'directory' ? 'Folder' : 'File'} details
					</p>
				</div>
			</div>
		</Dialog.Header>

		<div class="mt-6 space-y-4 text-sm">
			<div class="grid grid-cols-3 gap-2">
				<span class="text-muted-foreground col-span-1">Size</span>
				<span class="col-span-2 font-medium">{formatBytes(item.size)}</span>
			</div>

			<div class="grid grid-cols-3 gap-2">
				<span class="text-muted-foreground col-span-1">Type</span>
				<span class="col-span-2 font-medium">{item.type}</span>
			</div>

			<div class="grid grid-cols-3 gap-2">
				<span class="text-muted-foreground col-span-1">Location</span>
				<span class="col-span-2 truncate font-medium">{item.path}</span>
			</div>

			<div class="grid grid-cols-3 gap-2">
				<span class="text-muted-foreground col-span-1">Modified</span>
				<span class="col-span-2 font-medium">{formattedDate}</span>
			</div>
		</div>
	</Dialog.Content>
</Dialog.Root>