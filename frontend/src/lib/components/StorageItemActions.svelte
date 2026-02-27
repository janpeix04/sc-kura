<script lang="ts">
	import type { FileFolderPublic } from '$lib/client';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import type { StorageMode } from '$lib/schemas/types';
	import {
		EllipsisVertical,
		History,
		Trash2,
		ArrowDownToLine,
		PencilLine,
		Info
	} from '@lucide/svelte';
	import StorageItemInfo from './StorageItemInfo.svelte';

	let {
		mode = 'storage',
		item,
		onRestore,
		onDelete,
		onDownload,
		onRename,
		onRecycleBin
	}: {
		mode?: StorageMode;
		item: FileFolderPublic;
		onRestore?: () => void;
		onDelete?: () => void;
		onDownload?: () => void;
		onRename?: () => void;
		onRecycleBin?: (item_id: string) => void;
	} = $props();

	let showInfo = $state(false);
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger class="cursor-pointer">
		<EllipsisVertical class="text-foreground size-5" />
	</DropdownMenu.Trigger>
	<DropdownMenu.Content align="end">
		{#if mode === 'delete'}
			<DropdownMenu.Item class="flex cursor-pointer items-center" onclick={onRestore}>
				<History class="size-4" />
				Restore
			</DropdownMenu.Item>
			<DropdownMenu.Item class="flex cursor-pointer items-center" onclick={onDelete}>
				<Trash2 class="size-4" />
				Delete forever
			</DropdownMenu.Item>
		{:else}
			<DropdownMenu.Item class="flex cursor-pointer items-center" onclick={onDownload}>
				<ArrowDownToLine class="size-4" />
				Download
			</DropdownMenu.Item>
			<DropdownMenu.Item class="flex cursor-pointer items-center" onclick={onRename}>
				<PencilLine class="size-4" />
				Rename
			</DropdownMenu.Item>
			<DropdownMenu.Separator />
			<DropdownMenu.Item
				class="flex cursor-pointer items-center"
				onclick={() => {
					showInfo = true;
				}}
			>
				<Info class="size-4" />
				Info
			</DropdownMenu.Item>
			<DropdownMenu.Separator />
			<DropdownMenu.Item
				class="flex cursor-pointer items-center"
				onclick={() => onRecycleBin?.(item.id)}
			>
				<Trash2 class="size-4" />
				Delete
			</DropdownMenu.Item>
		{/if}
	</DropdownMenu.Content>
</DropdownMenu.Root>

<StorageItemInfo bind:open={showInfo} {item} />
