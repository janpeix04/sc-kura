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
	<!-- TODO: Compact view -->
{:else}
	<div
		class="flex cursor-pointer items-center gap-4 border-b border-gray-100 py-2 hover:bg-gray-50"
	>
		<a class="flex flex-1 items-center gap-4" href={localizeHref(`/folder/${file.id}`)}>
			<div class="flex flex-1 items-center gap-2">
				<span class="icon-[lucide--folder] size-5"></span>
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
