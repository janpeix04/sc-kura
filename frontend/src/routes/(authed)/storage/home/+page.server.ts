import {
	storageCreateFolderFolderNamePathPost,
	storageSuggestedFilesGet,
	storageSuggestedFoldersGet,
	storageUploadMultiplePathPost
} from '$lib/client';
import type { Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, depends }) => {
	depends('data:storage-home');
	const token = cookies.get('access_token');

	const { data: suggestedFolders } = await storageSuggestedFoldersGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		throwOnError: true
	});

	const { data: suggestedFiles } = await storageSuggestedFilesGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		throwOnError: true
	});

	return {
		suggestedFolders,
		suggestedFiles
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
		const folderName = data.get('folder_name') as string;
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
			return { success: false, createFolderError: error.msg };
		}
		return { success: false, uploadFilesError: 'Oops... Something went wrong!' };
	}
};
