import {
	cryptoBreadcrumbsFolderIdGet,
	cryptoFoldersFolderIdGet,
	storageAvailableSpaceGet
} from '$lib/client';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, params, depends }) => {
	depends('data:folder');

	const folderId = params.folderId;
	const token = cookies.get('access_token');

	const breadcrumbsPromise = cryptoBreadcrumbsFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: folderId
		}
	});

	const foldersPromise = cryptoFoldersFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: folderId
		}
	});

	const availableSpacePromise = storageAvailableSpaceGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const [{ data: breadcrumbs }, { data: folders }, { data: availableSpace }] = await Promise.all([
		breadcrumbsPromise,
		foldersPromise,
		availableSpacePromise
	]);

	return {
		breadcrumbs,
		folders,
		folderId,
		availableSpace
	};
};
