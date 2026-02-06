import { verifyAccountTokenPut } from "$lib/client/sdk.gen";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params, cookies }) => {
    const { data, error } = await verifyAccountTokenPut({
        path: {
            token: params.token
        }
    });
    if (!error) {
        return { success: data};
    }

    if ('msg' in error) {
        return { error: error.msg};
    }
}