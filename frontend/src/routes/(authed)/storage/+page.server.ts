import type { Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async() => {
    const items = [
        {
            name: "test",
            size: 1346,
            type: "directory",
            path: "/",
            lastModified: new Date()
        },
        {
            name: "folder",
            size: 23,
            type: "directory",
            path: "/",
            lastModified: new Date()
        },
        {
            name: "file",
            size: 546,
            type: "docx",
            path: "/",
            lastModified: new Date()
        },
        {
            name: "linguaskill",
            size: 2346,
            type: "directory",
            path: "/",
            lastModified: new Date()
        }
    ];

    return {
        items
    }
}

export const actions: Actions = {
    uploadFiles: async ({ request, cookies }) => {
        const data = await request.formData();
        const token = cookies.get('access_token');
    }
}