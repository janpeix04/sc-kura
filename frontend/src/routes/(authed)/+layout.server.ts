import { requireLogin } from "$lib/server/auth";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async () => {
    requireLogin();
}