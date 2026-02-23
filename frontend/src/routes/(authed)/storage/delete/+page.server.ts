import { storageDeletedFoldersGet, storageDeleteFilesGet } from "$lib/client";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({cookies}) => {
    const token = cookies.get('access_token');

    const { data: files } = await storageDeleteFilesGet({
        headers: {
            Authorization: `Bearer ${token}`
        },
        throwOnError: true
    });

    const { data: folders } = await storageDeletedFoldersGet({
        headers: {
            Authorization: `Bearer ${token}`
        },
        throwOnError: true
    });
    return {
        files,
        folders
    }
}