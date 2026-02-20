import type { Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	const segments = params.path === "" ? [] : params.path.split('/');
	const items = [
		{
			id: '1',
			name: 'test',
			size: 1346,
			type: 'directory',
			path: '/',
			lastModified: new Date()
		},
		{
			id: '2',
			name: 'folder',
			size: 23,
			type: 'directory',
			path: '/',
			lastModified: new Date()
		},
		{
			id: '3',
			name: 'file',
			size: 546,
			type: 'docx',
			path: '/',
			lastModified: new Date()
		},
		{
			id: '4',
			name: 'linguaskill',
			size: 2346,
			type: 'directory',
			path: '/',
			lastModified: new Date()
		},
		{
			id: '5',
			name: 'file2',
			size: 546765,
			type: 'docx',
			path: '/',
			lastModified: new Date()
		},
		{
			id: '6',
			name: 'file3',
			size: 546543543,
			type: 'docx',
			path: '/',
			lastModified: new Date()
		},
		{
			id: '7',
			name: 'file4',
			size: 546445323143,
			type: 'docx',
			path: '/',
			lastModified: new Date()
		}
	];

	return {
		items,
        segments
	};
};

export const actions: Actions = {
	uploadFiles: async ({ request, cookies }) => {
		const data = await request.formData();
		const token = cookies.get('access_token');
        console.log('data', data, 'token:', token)
	}
};
