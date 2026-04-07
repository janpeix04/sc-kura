<script lang="ts">
	import type { FolderPublic } from '$lib/client';
	import { Button } from '$lib/components/ui/button/index';
	import ActionsButton from './ActionsButton.svelte';

	let { folder }: { folder: FolderPublic } = $props();
</script>

<Button
	variant="folder"
	class="max-w-64 min-w-58 flex-1 items-center justify-between bg-search-background px-4 py-3 hover:bg-item-hover"
>
	<div class="flex gap-4">
		<span class="icon-[lucide--folder] size-5"></span>
		{folder.name}
	</div>

	<ActionsButton />
</Button>
