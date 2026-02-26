import { storageSuggestedFilesGet, storageSuggestedFoldersGet } from '$lib/client';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies }) => {
	const token = cookies.get('access_token');

    const { data: suggestedFolders } = await storageSuggestedFoldersGet({
        headers: {
            Authorization: `Bearer ${token}`
        },
        throwOnError: true
    });

    const { data: suggestedFiles } = await storageSuggestedFilesGet({
        headers: {
            Authorization: `Bearer ${token}`
        },
        throwOnError: true
    });

    return {
        suggestedFolders,
        suggestedFiles
    }
};
