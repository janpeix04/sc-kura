import type { Actions } from "@sveltejs/kit";

export const actions: Actions = {
    uploadFiles: async ({ request, cookies }) => {
        const data = await request.formData();
        const token = cookies.get('access_token');
    }
}