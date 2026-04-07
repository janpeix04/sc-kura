import type { ActionResult } from '@sveltejs/kit';
import { toast } from 'svelte-sonner';

export function superFormOnResult({
	result
}: {
	result: ActionResult;
	formEl: HTMLFormElement;
	formElement: HTMLFormElement;
	cancel: () => void;
}) {
	if (result.type === 'failure') {
		const form = result.data?.form;

		if (form.message) {
			toast.error(form.message);
		}
	}
	if (result.type === 'success') {
		const form = result.data?.form;

		if (form.message) {
			toast.success(form.message);
		}
	}
}
