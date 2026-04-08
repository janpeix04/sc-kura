<script lang="ts">
	import type { FolderPublic } from '$lib/client';
	import { Button } from '$lib/components/ui/button/index';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { formatBytes, formatDate } from '$lib/utilities/utils';
	import ActionsButton from './ActionsButton.svelte';

	let {
		folder,
		compact = false
	}: {
		folder: FolderPublic;
		compact?: boolean;
	} = $props();
</script>

{#if compact}
	<Button
		variant="folder"
		class="min-h-12 min-w-58 flex-1 items-center justify-between bg-search-background px-4 py-3 hover:bg-item-hover"
		href={localizeHref(`/folder/${folder.id}`)}
	>
		<div class="flex gap-4">
			<span class="icon-[lucide--folder] size-5"></span>
			{folder.name}
		</div>

		<ActionsButton item={folder} />
	</Button>
{:else}
	<div
		class="flex cursor-pointer items-center gap-4 border-b border-gray-100 py-2 hover:bg-gray-50"
	>
		<a class="flex flex-1 items-center gap-4" href={localizeHref(`/folder/${folder.id}`)}>
			<div class="flex flex-1 items-center gap-2">
				<span class="icon-[lucide--folder] size-5"></span>
				{folder.name}
			</div>
			<div class="w-48">
				<span class="text-sm">{folder.owner}</span>
			</div>
			<div class="w-36">
				<span class="text-sm">{formatDate(folder.modified_at)}</span>
			</div>
			<div class="w-24 text-right">
				<span class="text-sm">{formatBytes(folder.size)}</span>
			</div>
		</a>
		<div class="w-8">
			<ActionsButton item={folder} />
		</div>
	</div>
{/if}
