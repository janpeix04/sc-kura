import {
	cryptoFolderFolderIdDelete,
	storageEmptyTrashDelete,
	storageFileFileIdDelete,
	storageFolderFolderIdDelete,
	storageMoveToTrashFileFileIdPatch,
	storageMoveToTrashFolderFolderIdPatch,
	type FilePublic,
	type FolderPublic
} from '$lib/client';
import { toast } from 'svelte-sonner';
import { clientSideClient } from './client-side';
import type { DecryptedFolder } from '$lib/schemas/types';
import { m } from '$lib/paraglide/messages';

export function moveItemToTrash(item: FolderPublic | FilePublic) {
	const moveToTrash = [];
	if (item.type == 'directory') {
		moveToTrash.push(moveFolderToTrash(item.id));
	} else {
		moveToTrash.push(moveFileToTrash(item.id));
	}

	return Promise.all(moveToTrash);
}

async function moveFolderToTrash(folderId: string) {
	const { data } = await storageMoveToTrashFolderFolderIdPatch({
		client: clientSideClient,
		path: {
			folder_id: folderId
		},
		throwOnError: true
	});

	toast.success(data);
}

async function moveFileToTrash(folderId: string) {
	const { data } = await storageMoveToTrashFileFileIdPatch({
		client: clientSideClient,
		path: {
			file_id: folderId
		},
		throwOnError: true
	});

	toast.success(data);
}

export async function emptyTrash() {
	const { data } = await storageEmptyTrashDelete({
		client: clientSideClient,
		throwOnError: true
	});

	toast.success(data);
}

export function deleteItem(
	item: FolderPublic | FilePublic | DecryptedFolder,
	isEncrypted: boolean = false
) {
	const deleted = [];

	if (item.type === 'directory') {
		if (isEncrypted) {
			deleted.push(deleteEncryptedFolder(item.id));
		} else {
			deleted.push(deleteFolder(item.id));
		}
	} else {
		deleted.push(deleteFile(item.id));
	}

	return Promise.all(deleted);
}

async function deleteFolder(folderId: string) {
	const { data, error } = await storageFolderFolderIdDelete({
		client: clientSideClient,
		path: {
			folder_id: folderId
		}
	});

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	toast.success(data);
}

async function deleteFile(fileId: string) {
	const { data, error } = await storageFileFileIdDelete({
		client: clientSideClient,
		path: {
			file_id: fileId
		}
	});

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	toast.success(data);
}

async function deleteEncryptedFolder(folderId: string) {
	const { data, error } = await cryptoFolderFolderIdDelete({
		client: clientSideClient,
		path: {
			folder_id: folderId
		}
	});

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	toast.success(data);
}
