import {
	storageCreateFolderFolderNamePathPost,
	storageItemsFolderIdGet,
	storageUploadMultiplePathPost
} from '$lib/client';
import type { Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ parent, cookies, depends }) => {
	depends('data:my-files');
	const { root } = await parent();
	const token = cookies.get('access_token');

	const { data: items } = await storageItemsFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: root.id
		},
		throwOnError: true
	});

	return {
		folders: items.folders,
		files: items.files
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
