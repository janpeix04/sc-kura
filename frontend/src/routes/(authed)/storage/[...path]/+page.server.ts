import type { Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import {
	storageFilesPathGet,
	storageFoldersPathGet,
	storageUploadMultiplePathPost
} from '$lib/client';

export const load: PageServerLoad = async ({ params, cookies }) => {
	const segments = params.path === '' ? [] : params.path.split('/');
	const token = cookies.get('access_token');

	const path = segments.length === 0 ? '-' : [...segments].join('-');
	const { data: files } = await storageFilesPathGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: { path },
		throwOnError: true
	});

	const { data: folders } = await storageFoldersPathGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: { path },
        throwOnError: true
	});

	return {
		files,
        folders,
		segments
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
			return { success: false, uploadFilesError: error.msg};
		}
		return { success: false, uploadFilesError: "Oops... Something went wrong!"};
	}
};
