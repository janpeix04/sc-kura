<script lang="ts">
	import type { FolderPublic } from '$lib/client';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import { m } from '$lib/paraglide/messages';
	import ItemInfo from './ItemInfo.svelte';
	import RenameDialog from './RenameDialog.svelte';
	import { downloadItem } from '$lib/utilities/download';
	import { moveItemToTrash } from '$lib/utilities/delete';
	import { invalidatePage } from '$lib/utilities/utils';

	let {
		item
	}: {
		item: FolderPublic;
	} = $props();

	let openInfo = $state(false);
	let rename = $state(false);
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger class="flex cursor-pointer rounded-full p-1 hover:bg-more-hover">
		<span class="icon-[lucide--ellipsis-vertical] size-5"></span>
	</DropdownMenu.Trigger>
	<DropdownMenu.Content class="w-54">
		<DropdownMenu.Item class="cursor-pointer" onclick={() => downloadItem(item)}>
			<span class="icon-[lucide--arrow-down-to-line] size-4"></span>
			{m.download()}
		</DropdownMenu.Item>
		<DropdownMenu.Item class="cursor-pointer" onclick={() => (rename = true)}>
			<span class="icon-[lucide--square-pen] size-4"></span>
			{m.rename()}
		</DropdownMenu.Item>
		<DropdownMenu.Separator />
		<DropdownMenu.Item class="cursor-pointer" onclick={() => (openInfo = true)}>
			<span class="icon-[lucide--info] size-4"></span>
			{item.type === 'directory' ? m.folder_information() : m.file_information()}
		</DropdownMenu.Item>
		<DropdownMenu.Separator />
		<DropdownMenu.Item
			class="cursor-pointer"
			onclick={() => {
				moveItemToTrash(item).finally(invalidatePage);
			}}
		>
			<span class="icon-[lucide--trash-2] size-4"></span>
			{m.move_to_trash()}
		</DropdownMenu.Item>
	</DropdownMenu.Content>
</DropdownMenu.Root>

<ItemInfo bind:open={openInfo} {item} />
<RenameDialog bind:open={rename} {item} />
