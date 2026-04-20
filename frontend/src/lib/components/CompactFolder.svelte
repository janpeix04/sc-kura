<script lang="ts">
	import type { FolderPublic } from '$lib/client';
	import { localizeHref } from '$lib/paraglide/runtime';
	import ActionsButton from './ActionsButton.svelte';

	let {
		folder
	}: {
		folder: FolderPublic;
	} = $props();
</script>

<div
	class="h-11 max-w-64 min-w-58 flex items-center justify-between bg-search-background px-4 py-3 hover:bg-item-hover rounded-md"
>
	<a
		href={localizeHref(`/folder/${folder.id}`)}
		class="flex items-center gap-4 flex-1"
	>
		<span class="icon-[lucide--folder] size-5"></span>
		{folder.name}
	</a>

	<ActionsButton item={folder} />
</div>