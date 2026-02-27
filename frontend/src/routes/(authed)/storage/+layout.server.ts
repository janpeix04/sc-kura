import { storageRootGet } from "$lib/client";
import type { LayoutServerLoad } from "../$types";

export const load: LayoutServerLoad = async({ cookies }) => {
    const token = cookies.get('access_token');

    const { data: root } = await storageRootGet({
        headers: {
            Authorization: `Bearer ${token}`
        },
        throwOnError: true
    });
    
    return {
        root
    }
}