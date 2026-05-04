<script lang="ts">
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import { m } from '$lib/paraglide/messages';
	import RenameDialog from './RenameDialog.svelte';
	import type { DecryptedFolder, Mode } from '$lib/schemas/types';
	import EncryptedItemInfo from './EncryptedItemInfo.svelte';

	let {
		item,
		mode = 'storage',
		location
	}: {
		item: DecryptedFolder;
		mode?: Mode;
		location: string;
	} = $props();

	let openInfo = $state(false);
	let rename = $state(false);
	let deleteForever = $state(false);
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger class="flex cursor-pointer rounded-full p-1 hover:bg-more-hover">
		<span class="icon-[lucide--ellipsis-vertical] size-5"></span>
	</DropdownMenu.Trigger>
	<DropdownMenu.Content class="w-54">
		<DropdownMenu.Item class="cursor-pointer">
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
		<DropdownMenu.Item class="cursor-pointer" onclick={() => (deleteForever = true)}>
			<span class="icon-[lucide--trash-2] size-4"></span>
			{m.delete_forever()}
		</DropdownMenu.Item>
	</DropdownMenu.Content>
</DropdownMenu.Root>

<EncryptedItemInfo bind:open={openInfo} {item} {location} />
<RenameDialog bind:open={rename} {item} isEncrypted />
<!-- <DeleteDialog
	bind:isOpen={deleteForever}
	title={m.delete_forever_title()}
	description={m.delete_forever_description()}
	confirm={m.permanently_delete()}
	onClick={() => {
		deleteItem(item).finally(invalidatePage);
		deleteForever = false;
	}}
/> -->
