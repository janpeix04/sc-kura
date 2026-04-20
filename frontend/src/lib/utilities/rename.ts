import {
	storageRenameFileFileIdPatch,
	storageRenameFolderFolderIdPatch,
	type FilePublic,
	type FolderPublic
} from '$lib/client';
import { toast } from 'svelte-sonner';
import { clientSideClient } from './client-side';

export function renameItem(item: FolderPublic | FilePublic, new_name: string) {
	const renames = [];
	if (item.type == 'directory') {
		renames.push(renameFolder(item.id, new_name));
	} else {
		renames.push(renameFile(item.id, new_name));
	}

	return Promise.all(renames);
}

async function renameFolder(folderId: string, new_name: string) {
	const { data } = await storageRenameFolderFolderIdPatch({
		client: clientSideClient,
		path: {
			folder_id: folderId
		},
		body: {
			name: new_name
		},
		throwOnError: true
	});

	toast.success(data);
}

async function renameFile(folderId: string, new_name: string) {
	const { data } = await storageRenameFileFileIdPatch({
		client: clientSideClient,
		path: {
			file_id: folderId
		},
		body: {
			name: new_name
		},
		throwOnError: true
	});

	toast.success(data);
}
