import {
	cryptoRenameFileFileIdPatch,
	cryptoRenameFolderFolderIdPatch,
	storageRenameFileFileIdPatch,
	storageRenameFolderFolderIdPatch,
	type FilePublic,
	type FolderPublic
} from '$lib/client';
import { toast } from 'svelte-sonner';
import { clientSideClient } from './client-side';
import type { DecryptedFolder } from '$lib/schemas/types';
import { m } from '$lib/paraglide/messages';
import { arrayBufferToBase64, encryptFile } from '$lib/crypto';

export function renameItem(
	item: FolderPublic | FilePublic | DecryptedFolder,
	newName: string,
	isEncrypted: boolean
) {
	const renames = [];
	if (item.type == 'directory') {
		if (isEncrypted && 'key' in item) {
			renames.push(renameEncryptedFolder(item.id, newName, item.key));
		} else if (!isEncrypted) {
			renames.push(renameFolder(item.id, newName));
		}
	} else {
		if (isEncrypted && 'key' in item) {
			renames.push(renameEncryptedFile(item.id, newName, item.key));
		} else {
			renames.push(renameFile(item.id, newName));
		}
	}

	return Promise.all(renames);
}

async function renameFolder(folderId: string, newName: string) {
	const { data, error } = await storageRenameFolderFolderIdPatch({
		client: clientSideClient,
		path: {
			folder_id: folderId
		},
		body: {
			name: newName
		}
	});

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	toast.success(data);
}

async function renameFile(folderId: string, newName: string) {
	const { data, error } = await storageRenameFileFileIdPatch({
		client: clientSideClient,
		path: {
			file_id: folderId
		},
		body: {
			name: newName
		}
	});

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	toast.success(data);
}

async function renameEncryptedFolder(folderId: string, newName: string, key: CryptoKey) {
	const nameEncoded = new TextEncoder().encode(newName);
	const { iv, encrypted } = await encryptFile(key, nameEncoded.buffer);

	const { data, error } = await cryptoRenameFolderFolderIdPatch({
		client: clientSideClient,
		path: {
			folder_id: folderId
		},
		body: {
			encrypted_name: arrayBufferToBase64(encrypted),
			iv: arrayBufferToBase64(iv)
		}
	});

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	toast.success(data);
}

async function renameEncryptedFile(fileId: string, newName: string, key: CryptoKey) {
	const nameEncoded = new TextEncoder().encode(newName);
	const { iv, encrypted } = await encryptFile(key, nameEncoded.buffer);

	const { data, error } = await cryptoRenameFileFileIdPatch({
		client: clientSideClient,
		path: {
			file_id: fileId
		},
		body: {
			encrypted_name: arrayBufferToBase64(encrypted),
			iv: arrayBufferToBase64(iv)
		}
	});

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	toast.success(data);
}
