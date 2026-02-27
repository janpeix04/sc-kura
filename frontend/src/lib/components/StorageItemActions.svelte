<script lang="ts">
	import { storageMoveToTrashFileFileIdPatch, storageMoveToTrashFolderFolderIdPatch, type FileFolderPublic } from '$lib/client';
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
	import { createClient } from '$lib/client/client';
	import { toast } from 'svelte-sonner';
	import { invalidate } from '$app/navigation';
	import { page } from '$app/state';

	let {
		mode = 'storage',
		item,
		onRestore,
		onDelete,
		onDownload,
		onRename,
	}: {
		mode?: StorageMode;
		item: FileFolderPublic;
		onRestore?: () => void;
		onDelete?: () => void;
		onDownload?: () => void;
		onRename?: () => void;
	} = $props();

	const client = createClient({baseUrl: ''});

	let showInfo = $state(false);

	async function moveFolderToTrash(folderId: string) {
		const { data } = await storageMoveToTrashFolderFolderIdPatch({
			client,
			path: {
				folder_id: folderId
			},
			throwOnError: true
		});
		toast.success(data);
	}

	async function moveFileToTrash(fileId: string) {
		const { data } = await storageMoveToTrashFileFileIdPatch({
			client,
			path: {
				file_id: fileId
			},
			throwOnError: true
		});
		toast.success(data);
	}
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
				onclick={async () => {
					if (item.type === 'directory') {
						await moveFolderToTrash(item.id);
					} else {
						await moveFileToTrash(item.id);
					}
					const pathname = page.url.pathname;
					if (pathname.startsWith('/storage/folder')) {
						invalidate('data:folder')
					}
					if (pathname.startsWith('/storage/home')) {
						invalidate('data:storage-home');
					}
					if (pathname.startsWith('/storage/my-files')) {
						invalidate('data:my-files');
					}
				}}
			>
				<Trash2 class="size-4" />
				Delete
			</DropdownMenu.Item>
		{/if}
	</DropdownMenu.Content>
</DropdownMenu.Root>

<StorageItemInfo bind:open={showInfo} {item} />
