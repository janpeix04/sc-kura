import {
	cryptoBreadcrumbsFolderIdGet,
	cryptoFilesFolderIdGet,
	cryptoFoldersFolderIdGet,
	cryptoLocationFolderFolderIdGet,
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

	const filesPromise = cryptoFilesFolderIdGet({
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

	const locationPromise = cryptoLocationFolderFolderIdGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
		path: {
			folder_id: folderId
		},
		throwOnError: true
	});

	const [
		{ data: breadcrumbs },
		{ data: folders },
		{ data: files },
		{ data: availableSpace },
		{ data: location }
	] = await Promise.all([
		breadcrumbsPromise,
		foldersPromise,
		filesPromise,
		availableSpacePromise,
		locationPromise
	]);

	return {
		breadcrumbs,
		folderId,
		folders,
		files,
		availableSpace,
		location
	};
};
