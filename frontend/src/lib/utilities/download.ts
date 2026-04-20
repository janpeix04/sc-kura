import {
	storageDownloadFileFileIdGet,
	storageDownloadFolderFolderIdGet,
	type FilePublic,
	type FolderPublic
} from '$lib/client';
import { clientSideClient } from './client-side';

function downloadBlob(blob: Blob, itemName: string) {
	const url = window.URL.createObjectURL(blob);
	const a = document.createElement('a');

	a.href = url;
	a.download = itemName;

	document.body.appendChild(a);

	a.click();
	a.remove();

	window.URL.revokeObjectURL(url);
}

export function downloadItem(item: FolderPublic | FilePublic) {
	const downloads = [];
	if (item.type == 'directory') {
		downloads.push(downloadFolder(item.id, item.name));
	} else {
		downloads.push(downloadFile(item.id, item.name));
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
