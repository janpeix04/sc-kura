import type { Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import {
	storageCreateFolderFolderNamePathPost,
	storageItemsFolderIdGet,
	storageUploadMultiplePathPost
} from '$lib/client';

export const load: PageServerLoad = async ({ params, cookies }) => {
	const folderId = params.folder_id;
	const token = cookies.get('access_token');

	const { data: items } = await storageItemsFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: { folder_id: folderId },
		throwOnError: true
	});

	return {
		items,
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
