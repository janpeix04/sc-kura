<script lang="ts">
	import {
		storageDeleteFileFileIdDelete,
		storageDeleteFolderFolderIdDelete,
		storageDownloadFileFileIdGet,
		storageDownloadFolderFolderIdGet,
		storageMoveToTrashFileFileIdPatch,
		storageMoveToTrashFolderFolderIdPatch,
		storageRestoreFileFileIdPatch,
		storageRestoreFolderFolderIdPatch,
		type FileFolderPublic
	} from '$lib/client';
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
	import StorageRenameDialog from './StorageRenameDialog.svelte';
	import { downloadBlob, invalidatePages } from '$lib/utilities/storage';
	import { page } from '$app/state';

	let {
		mode = 'storage',
		item
	}: {
		mode?: StorageMode;
		item: FileFolderPublic;
	} = $props();

	const client = createClient({ baseUrl: '' });

	let showInfo = $state(false);
	let rename = $state(false);

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

	async function downloadFile(fileId: string, fileName: string) {
		const { data } = await storageDownloadFileFileIdGet({
			client,
			path: {
				file_id: fileId
			},
			throwOnError: true
		});
		downloadBlob(data, fileName);
	}

	async function downloadFolder(folderId: string, folderName: string) {
		const { data } = await storageDownloadFolderFolderIdGet({
			client,
			path: {
				folder_id: folderId
			},
			throwOnError: true
		});
		downloadBlob(data, folderName);
	}

	async function restoreFile(fileID: string) {
		const { data } = await storageRestoreFileFileIdPatch({
			client,
			path: {
				file_id: fileID
			},
			throwOnError: true
		});
		toast.success(data);
	}

	async function restoreFolder(folderId: string) {
		const { data } = await storageRestoreFolderFolderIdPatch({
			client,
			path: {
				folder_id: folderId
			},
			throwOnError: true
		});
		toast.success(data);
	}

	async function deleteFileForever(fileId: string) {
		const { data } = await storageDeleteFileFileIdDelete({
			client,
			path: {
				file_id: fileId
			},
			throwOnError: true
		});
		toast.success(data);
	}

	async function deleteFolderForever(folderId: string) {
		const { data } = await storageDeleteFolderFolderIdDelete({
			client,
			path: {
				folder_id: folderId
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
			<DropdownMenu.Item
				class="flex cursor-pointer items-center"
				onclick={async () => {
					if (item.type === 'directory') {
						await restoreFolder(item.id);
					} else {
						await restoreFile(item.id);
					}
					invalidatePages(page.url.pathname);
				}}
			>
				<History class="size-4" />
				Restore
			</DropdownMenu.Item>
			<DropdownMenu.Item class="flex cursor-pointer items-center" onclick={async () => {
				if (item.type === 'directory') {
					await deleteFolderForever(item.id);
				} else {
					await deleteFileForever(item.id);
				}
				invalidatePages(page.url.pathname);
			}}>
				<Trash2 class="size-4" />
				Delete forever
			</DropdownMenu.Item>
		{:else}
			<DropdownMenu.Item
				class="flex cursor-pointer items-center"
				onclick={async () => {
					if (item.type === 'directory') {
						await downloadFolder(item.id, item.name);
					} else {
						await downloadFile(item.id, item.name);
					}
				}}
			>
				<ArrowDownToLine class="size-4" />
				Download
			</DropdownMenu.Item>
			<DropdownMenu.Item class="flex cursor-pointer items-center" onclick={() => (rename = true)}>
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
					invalidatePages(page.url.pathname);
				}}
			>
				<Trash2 class="size-4" />
				Delete
			</DropdownMenu.Item>
		{/if}
	</DropdownMenu.Content>
</DropdownMenu.Root>

<StorageItemInfo bind:open={showInfo} {item} />
<StorageRenameDialog bind:open={rename} {item} />
