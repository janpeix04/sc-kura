import { storageUploadFilesFolderIdPost, type CeleryTaskResponse } from '$lib/client';
import { clientSideClient } from './client-side';

export async function uploadFiles(files: FileList, parentId: string): Promise<CeleryTaskResponse> {
	const { data } = await storageUploadFilesFolderIdPost({
		client: clientSideClient,
		path: {
			folder_id: parentId
		},
		body: {
			files: Array.from(files)
		},
		throwOnError: true
	});
	console.log('Upload response:', data);

	return data;
}
