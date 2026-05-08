import {
	cryptoDownloadFileFileIdGet,
	cryptoDownloadFolderFolderIdGet,
	storageDownloadFileFileIdGet,
	storageDownloadFolderFolderIdGet,
	type FilePublic,
	type FolderPublic
} from '$lib/client';
import { toast } from 'svelte-sonner';
import { clientSideClient } from './client-side';
import { m } from '$lib/paraglide/messages';
import type { DecryptedFile, DecryptedFolder } from '$lib/schemas/types';
import { get } from 'svelte/store';
import { privateKey } from '$lib/stores/crypto';
import { base64ToArrayBuffer, decryptFile, unwrapKey } from '$lib/crypto';
import { buildZipFromTree, decryptFolderTree } from './utils';

export function downloadBlob(blob: Blob, itemName: string) {
	const url = window.URL.createObjectURL(blob);
	const a = document.createElement('a');

	a.href = url;
	a.download = itemName;

	document.body.appendChild(a);

	a.click();
	a.remove();

	window.URL.revokeObjectURL(url);
}

export function downloadItem(
	item: FolderPublic | FilePublic | DecryptedFile | DecryptedFolder,
	filename: string,
	isEncrypted: boolean
) {
	const downloads = [];
	if (item.type == 'directory') {
		if (isEncrypted) {
			downloads.push(downloadEncryptedFolder(item.id));
		} else {
			downloads.push(downloadFolder(item.id, filename));
		}
	} else {
		if (isEncrypted) {
			downloads.push(downloadEncryptedFile(item.id, filename));
		} else {
			downloads.push(downloadFile(item.id, filename));
		}
	}

	return Promise.all(downloads);
}

async function downloadFolder(folderId: string, filename: string) {
	const { data } = await storageDownloadFolderFolderIdGet({
		client: clientSideClient,
		path: {
			folder_id: folderId
		},
		throwOnError: true
	});
	downloadBlob(data, filename);
}

async function downloadFile(fileId: string, filename: string) {
	const { data } = await storageDownloadFileFileIdGet({
		client: clientSideClient,
		path: {
			file_id: fileId
		},
		throwOnError: true
	});
	downloadBlob(data, filename);
}

async function downloadEncryptedFile(fileId: string, filename: string) {
	const priv = get(privateKey);

	if (!priv) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	const { data, error, response } = await cryptoDownloadFileFileIdGet({
		client: clientSideClient,
		path: {
			file_id: fileId
		}
	});

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	const wrappedKey = response.headers.get('x-encrypted-key');
	const fileIv = response.headers.get('x-iv');

	if (wrappedKey === null || fileIv === null) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	const wrappedKeyBuffer = base64ToArrayBuffer(wrappedKey);
	const key = await unwrapKey(wrappedKeyBuffer, priv);

	const encryptedBuffer = await data.arrayBuffer();
	const iv = base64ToArrayBuffer(fileIv);

	const decryptedBuffer = await decryptFile(key, iv, encryptedBuffer);
	const blob = new Blob([decryptedBuffer]);

	downloadBlob(blob, filename);
}

async function downloadEncryptedFolder(folderId: string) {
	const priv = get(privateKey);

	if (!priv) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	const { data, error } = await cryptoDownloadFolderFolderIdGet({
		client: clientSideClient,
		path: {
			folder_id: folderId
		}
	});

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	const root = await decryptFolderTree(data, priv);
	const blob = await buildZipFromTree(root);

	downloadBlob(blob, `${root.name}.zip`);
}
