import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, cookies }) => {
	const segments = params.path === '' ? [] : params.path.split('/');
	return {
		segments
	};
};
