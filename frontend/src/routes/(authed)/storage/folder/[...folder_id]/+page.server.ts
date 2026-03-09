import type { Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import {
	storageCreateFolderFolderNamePathPost,
	storageItemsFolderIdGet,
	storageUploadMultiplePathPost
} from '$lib/client';
import { getStorageStatus, parseStorageFolderId } from '$lib/utilities/storage';

export const load: PageServerLoad = async ({ params, cookies, depends }) => {
	depends('data:folder');
	const { folderId, status } = parseStorageFolderId(params.folder_id);
	const token = cookies.get('access_token');

	const { data: items } = await storageItemsFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: { folder_id: folderId },
		query: {
			status: getStorageStatus(status)
		},
		throwOnError: true
	});

	return {
		folders: items.folders,
		files: items.files,
		status
	};
};

export const actions: Actions = {
	uploadFiles: async ({ request, cookies }) => {
		const data = await request.formData();
		const token = cookies.get('access_token');

		const files = data.getAll('files') as Array<File>;
		const { data: uploadFilesResult, error } = await storageUploadMultiplePathPost({
			headers: {
				Authorization: `Bearer ${token}`
			},
			body: { files },
			path: {
				path: data.get('path') as string
			}
		});
		if (!error) {
			return { success: true, uploadFilesResult };
		}
		if ('msg' in error) {
			return { success: false, uploadFilesError: error.msg };
		}
		return { success: false, uploadFilesError: 'Oops... Something went wrong!' };
	},
	createFolder: async ({ request, cookies }) => {
		const data = await request.formData();
		const token = cookies.get('access_token');
		const folderName = data.get("folder_name") as string;
		const path = data.get('path') as string;

		const { data: createFolderResult, error } = await storageCreateFolderFolderNamePathPost({
			headers: {
				Authorization: `Bearer ${token}`
			},
			path: {
				folder_name: folderName,
				path
			}
		});

		if (!error) {
			return { success: true, createFolderResult };
		}
		if ('msg' in error) {
			return { success: false, createFolderError: error.msg};
		}
		return { success: false, uploadFilesError: 'Oops... Something went wrong!' };
	}
};
