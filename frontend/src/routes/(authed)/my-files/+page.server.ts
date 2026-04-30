import {
	storageFoldersFolderIdGet,
	type FolderPublic,
	storageFilesFolderIdGet,
	storageAvailableSpaceGet
} from '$lib/client';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, parent, depends }) => {
	depends('data:my-files');

	const token = cookies.get('access_token');
	const root = (await parent()).root as FolderPublic;

	const foldersPromise = storageFoldersFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: root.id
		}
	});

	const filesPromise = storageFilesFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: root.id
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
		folderId: root!.id,
		availableSpace
	};
};
