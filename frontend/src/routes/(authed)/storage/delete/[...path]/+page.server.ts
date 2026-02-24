import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	const segments = params.path === '' ? [] : params.path.split('/');
	return {
		segments
	};
};
