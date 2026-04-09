import {
	storageUploadChunkPost,
	storageUploadCompleteFolderIdPost,
	storageUploadFileFolderIdPost
} from '$lib/client';
import { toast } from 'svelte-sonner';
import { clientSideClient } from './client-side';
import { m } from '$lib/paraglide/messages';

export const MAX_SIZE = 10 * 1024 * 1024;
export const CHUNK_SIZE = 5 * 1024 * 1024;

export async function uploadFile(file: File, parentId: string) {
	if (file.size < MAX_SIZE) {
		return uploadDirect(file, parentId);
	} else {
		uploadChunked(file, parentId);
	}
}

export async function uploadFiles(files: FileList, parentId: string) {
	const uploads = [];

	for (const file of files) {
		uploads.push(uploadFile(file, parentId));
	}

	return Promise.all(uploads);
}

async function uploadDirect(file: File, parentId: string) {
	const { data, error } = await storageUploadFileFolderIdPost({
		client: clientSideClient,
		path: {
			folder_id: parentId
		},
		body: {
			file
		}
	});

	if (!error) {
		toast.success(data);
	}

	if (error === undefined) return;
	if ('msg' in error) {
		return toast.error(error.msg);
	}
	return toast.error(m.oops_something_went_wrong());
}

async function uploadChunked(file: File, parentId: string) {
	const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
	const uploadId = crypto.randomUUID();

	for (let i = 0; i < totalChunks; i++) {
		const start = i * CHUNK_SIZE;
		const end = Math.min(start + CHUNK_SIZE, file.size);

		const chunk = file.slice(start, end);

		const { data } = await storageUploadChunkPost({
			client: clientSideClient,
			body: {
				chunk,
				upload_id: uploadId,
				index: i
			},
			throwOnError: true
		});
		toast.success(data);
	}

	const { data } = await storageUploadCompleteFolderIdPost({
		client: clientSideClient,
		path: {
			folder_id: parentId
		},
		body: {
			total_chunks: totalChunks,
			upload_id: uploadId,
			filename: file.name
		},
		throwOnError: true
	});
	toast.success(data);
}
