<script lang="ts">
	import { Folder, File } from '@lucide/svelte';
	import { Button } from './ui/button';
	import type { FileFolderPublic } from '$lib/client';

	let {
		segments,
		item,
		basePath
	}: {
		segments: string[];
		item: FileFolderPublic;
		basePath?: string;
	} = $props();
</script>

{#if item.type === 'directory'}
	<Button
		variant="outline"
		class="bg-background2 flex w-64 flex-row items-center justify-start py-5"
		href={`${basePath}/${[...segments, item.name].join('/')}`}
	>
		<Folder class="size-5 shrink-0" />
		<span class="flex-1 truncate text-left font-medium">{item.name}</span>
	</Button>
{:else}
	<Button
		variant="ghost"
		class="bg-background2 flex h-48 w-48 flex-col overflow-hidden rounded-lg pb-4 shadow sm:h-56 sm:w-56 md:h-64 md:w-64"
	>
		<div class="flex gap-4 self-start p-2">
			{#if item.type === 'directory'}
				<Folder class="size-5 shrink-0" />
			{:else}
				<File class="size-5 shrink-0" />
			{/if}
			<span class="flex-1 truncate text-left font-medium">{item.name}</span>
		</div>

		<div class="flex w-full flex-1 items-center justify-center rounded-lg bg-white">
			<span class="text-sm text-gray-400">Preview</span>
		</div>
	</Button>
{/if}
