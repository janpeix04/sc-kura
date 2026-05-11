import type { PageServerLoad } from './$types';
import {
	storageAvailableSpaceGet,
	storageSuggestedFilesGet,
	storageSuggestedFoldersGet
} from '$lib/client';

export const load: PageServerLoad = async ({ cookies, parent, depends }) => {
	depends('data:home');

	const token = cookies.get('access_token');
	const root = (await parent()).root;

	const suggestedFoldersPromise = storageSuggestedFoldersGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const suggestedFilesPromise = storageSuggestedFilesGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const availableSpacePromise = storageAvailableSpaceGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const [{ data: suggestedFolders }, { data: suggestedFiles }, { data: availableSpace }] =
		await Promise.all([suggestedFoldersPromise, suggestedFilesPromise, availableSpacePromise]);

	return {
		suggestedFolders,
		suggestedFiles,
		folderId: root!.id,
		availableSpace
	};
};
