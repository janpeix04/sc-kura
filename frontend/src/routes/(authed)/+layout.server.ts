import { storageFolderRootGet } from '$lib/client';
import { requireLogin } from '$lib/server/auth';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, locals }) => {
	const user = requireLogin();

	const token = cookies.get('access_token');

	const rootPromise = storageFolderRootGet({
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	const [{ data: root }] = await Promise.all([rootPromise]);
	
	return {
		user,
		root
	};
};
