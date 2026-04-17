import {
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

export function deleteItem(item: FolderPublic | FilePublic) {
	const deleted = [];

	if (item.type === 'directory') {
		deleted.push(deleteFolder(item.id));
	} else {
		deleted.push(deleteFile(item.id));
	}

	return Promise.all(deleted);
}

async function deleteFolder(folderId: string) {
	const { data } = await storageFolderFolderIdDelete({
		client: clientSideClient,
		path: {
			folder_id: folderId
		},
		throwOnError: true
	});

	toast.success(data);
}

async function deleteFile(fileId: string) {
	const { data } = await storageFileFileIdDelete({
		client: clientSideClient,
		path: {
			file_id: fileId
		},
		throwOnError: true
	});

	toast.success(data);
}
