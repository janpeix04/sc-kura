import type { PageServerLoad } from "../$types";

export const load: PageServerLoad = async ({url}) => {
    const origin = url.searchParams.get('origin');
    const message = url.searchParams.get('message');
    
    if (origin && message) {
        return {
            origin,
            message
        }
    }
}