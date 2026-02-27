import { storageDeleteItemsGet } from "$lib/client";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({cookies, depends}) => {
    depends('data:trash');
    const token = cookies.get('access_token');

    const { data: items } = await storageDeleteItemsGet({
        headers: {
            Authorization: `Bearer ${token}`
        },
        throwOnError: true
    });

    return {
        items
    }
}