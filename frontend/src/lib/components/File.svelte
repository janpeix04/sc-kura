<script lang="ts">
	import type { FilePublic } from '$lib/client';
	import { Button } from '$lib/components/ui/button/index';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { formatBytes, formatDate } from '$lib/utilities/utils';
	import ActionsButton from './ActionsButton.svelte';

	let {
		file,
		compact = false
	}: {
		file: FilePublic;
		compact?: boolean;
	} = $props();
</script>

{#if compact}
	<Button
		variant="folder"
		class="min-h-12 max-w-64 min-w-58 flex-1 items-center justify-between bg-search-background px-4 py-3 hover:bg-item-hover"
		href={localizeHref(`/folder/${file.id}`)}
	>
		<div class="flex gap-4">
			<span class="icon-[lucide--file] size-5"></span>
			{file.name}
		</div>

		<ActionsButton item={file} />
	</Button>
{:else}
	<div
		class="flex cursor-pointer items-center gap-4 border-b border-gray-100 py-2 hover:bg-gray-50"
	>
		<a class="flex flex-1 items-center gap-4" href={localizeHref(`/folder/${file.parent_id}`)}>
			<div class="flex flex-1 items-center gap-2">
				<span class="icon-[lucide--file] size-5"></span>
				{file.name}
			</div>
			<div class="w-48">
				<span class="text-sm">{file.owner}</span>
			</div>
			<div class="w-36">
				<span class="text-sm">{formatDate(file.modified_at)}</span>
			</div>
			<div class="w-24 text-right">
				<span class="text-sm">{formatBytes(file.size)}</span>
			</div>
		</a>
		<div class="w-8">
			<ActionsButton item={file} />
		</div>
	</div>
{/if}
