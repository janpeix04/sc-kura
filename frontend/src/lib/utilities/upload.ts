import { storageUploadFolderIdPost } from '$lib/client';
import { toast } from 'svelte-sonner';
import { clientSideClient } from './client-side';

export async function uploadFiles(files: FileList, parentId: string) {
	const uploads = [];

	for (const file of files) {
		uploads.push(uploadFile(file, parentId));
	}

	return Promise.all(uploads);
}

async function uploadFile(file: File, parentId: string) {
	const { data } = await storageUploadFolderIdPost({
		client: clientSideClient,
		path: {
			folder_id: parentId
		},
		body: {
			file
		},
		throwOnError: true
	});

	toast.success(data);
}
