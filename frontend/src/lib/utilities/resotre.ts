import {
	storageRestoreFileFileIdPatch,
	storageRestoreFolderFolderIdPatch,
	type FilePublic,
	type FolderPublic
} from '$lib/client';
import { toast } from 'svelte-sonner';
import { clientSideClient } from './client-side';

export function restoreItem(item: FolderPublic | FilePublic) {
	const restore = [];

	if (item.type === 'directory') {
		restore.push(restoreFolder(item.id));
	} else {
		restore.push(restoreFile(item.id));
	}

	return Promise.all(restore);
}

async function restoreFolder(folderId: string) {
	const { data } = await storageRestoreFolderFolderIdPatch({
		client: clientSideClient,
		path: {
			folder_id: folderId
		},
		throwOnError: true
	});

	toast.success(data);
}

async function restoreFile(fileId: string) {
	const { data } = await storageRestoreFileFileIdPatch({
		client: clientSideClient,
		path: {
			file_id: fileId
		},
		throwOnError: true
	});

	toast.success(data);
}
