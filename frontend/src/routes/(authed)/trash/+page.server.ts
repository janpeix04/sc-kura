import {
	storageFoldersFolderIdGet,
	storageFilesFolderIdGet,
	storageAvailableSpaceGet,
	storageFolderTrashGet
} from '$lib/client';
import { superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { zod4 } from 'sveltekit-superforms/adapters';

export const load: PageServerLoad = async ({ cookies, depends }) => {
	depends('data:trash');

	const token = cookies.get('access_token');
	const { data: trash } = await storageFolderTrashGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		throwOnError: true
	});

	const foldersPromise = storageFoldersFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: trash.id
		},
		query: {
			status: 'deleted'
		}
	});

	const filesPromise = storageFilesFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: trash.id
		},
		query: {
			status: 'deleted'
		}
	});

	const availableSpacePromise = storageAvailableSpaceGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const [{ data: folders }, { data: files }, { data: availableSpace }] = await Promise.all([
		foldersPromise,
		filesPromise,
		availableSpacePromise
	]);

	return {
		folders,
		files,
		folderId: trash.id,
		availableSpace
	};
};
