import type { PageServerLoad } from './$types';
import { storageDeletedItemsPathGet } from '$lib/client';

export const load: PageServerLoad = async ({ params, cookies }) => {
	const segments = params.path === '' ? [] : params.path.split('/');
	const token = cookies.get('access_token');

	const { data: items } = await storageDeletedItemsPathGet({
		headers: {
			Authorization: `Bearer ${token}`
		},
        path: {
            path: segments.length === 0 ? '-' : segments.join('-')
        },
		throwOnError: true
	});

	return {
		items,
		segments
	};
};
