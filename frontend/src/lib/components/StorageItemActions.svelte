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

	let {
		mode = 'storage',
		item,
		onRestore,
		onDelete,
		onDownload,
		onRename,
		onInfo,
		onRecycleBin
	}: {
		mode: StorageMode;
		item: FileFolderPublic;
		onRestore?: () => void;
		onDelete?: () => void;
		onDownload?: () => void;
		onRename?: () => void;
		onInfo?: () => void;
		onRecycleBin?: (item_id: string) => void;
	} = $props();
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger class="absolute right-5 cursor-pointer">
		<EllipsisVertical class="size-5" />
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
			<DropdownMenu.Item class="flex cursor-pointer items-center" onclick={onInfo}>
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
