import { tasksTaskIdGet, type CeleryTaskResponse } from '$lib/client';
import { getLocale } from '$lib/paraglide/runtime';
import { clientSideClient } from './client-side';

export function getUserInitials(firstName: string, lastName: string) {
	const firstInitial = firstName[0].toUpperCase();
	const lastInitial = lastName[0].toUpperCase();
	return firstInitial + lastInitial;
}

export function capitalize(text: string) {
	return text[0].toUpperCase() + text.slice(1);
}

export function formatBytes(bytes: number, decimals: number = 2) {
	if (bytes === 0) return '0 B';

	const k = 1024;
	const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
	const i = Math.floor(Math.log(bytes) / Math.log(k));

	const value = bytes / Math.pow(k, i);

	return `${value.toFixed(decimals)} ${sizes[i]}`;
}

export function formatDate(date: string) {
	const d = new Date(date);

	return d.toLocaleDateString(getLocale(), {
		month: 'short',
		day: 'numeric',
		year: 'numeric'
	});
}

export async function getStatus(taskId: string): Promise<CeleryTaskResponse> {
	const { data } = await tasksTaskIdGet({
		client: clientSideClient,
		path: {
			task_id: taskId
		},
		throwOnError: true
	});

	return data;
}
