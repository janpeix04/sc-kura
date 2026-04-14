<script lang="ts">
	import type { FilePublic, FolderPublic } from '$lib/client';
	import { formatBytes, formatDate } from '$lib/utilities/utils';
	import type { Snippet } from 'svelte';

	let {
		item,
		actions,
		onClick
	}: {
		item: FilePublic | FolderPublic;
		actions: Snippet;
		onClick?: () => void;
	} = $props();
</script>

<div
	class="group contents cursor-pointer"
	onclick={onClick}
	role="button"
	tabindex="0"
	onkeydown={(e) => e.key === 'Enter' && onClick?.()}
>
	<div class="flex items-center gap-2 truncate border-b p-2 group-hover:bg-gray-50">
		{#if item.type === 'directory'}
			<span class="icon-[lucide--folder] size-5"></span>
		{:else}
			<span class="icon-[lucide--file] size-5"></span>
		{/if}
		{item.name}
	</div>
	<div class="border-b p-2 group-hover:bg-gray-50">{item.owner}</div>
	<div class="border-b p-2 group-hover:bg-gray-50">{formatDate(item.modified_at)}</div>
	<div class="border-b p-2 group-hover:bg-gray-50">{formatBytes(item.size)}</div>
	<div class="flex justify-center border-b p-2 group-hover:bg-gray-50">
		{@render actions()}
	</div>
</div>
