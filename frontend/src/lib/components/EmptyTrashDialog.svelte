<script lang="ts">
	import { storageDeleteAllDelete } from '$lib/client';
	import { createClient } from '$lib/client/client';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { toast } from 'svelte-sonner';
	import { Button } from './ui/button';
	import { invalidatePages } from '$lib/utilities/storage';
	import { page } from '$app/state';

	let {
		open = $bindable(),
	}: {
		open: boolean;
	} = $props();

	const client = createClient({ baseUrl: '' });

	async function emptyTrash() {
		const { data } = await storageDeleteAllDelete({
			client,
			throwOnError: true
		});
		toast.success(data);
		invalidatePages(page.url.pathname);
		open = false;
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content showCloseButton={false}>
		<Dialog.Header>
			<Dialog.Title>Delete forever?</Dialog.Title>
		</Dialog.Header>
		All items in bin will be deleted forever. This can't be undone.
		<div class="flex justify-end gap-2">
			<Button variant="outline" onclick={() => (open = false)}>Cancel</Button>
			<Button
				class="bg-semantic-error cursor-pointer text-white hover:bg-red-400"
				onclick={async () => {
					emptyTrash();
				}}>Delete</Button
			>
		</div>
	</Dialog.Content>
</Dialog.Root>
