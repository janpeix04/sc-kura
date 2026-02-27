<script lang="ts">
	import {
		storageRenameFileFileIdPatch,
		storageRenameFolderFolderIdPatch,
		type FileFolderPublic
	} from '$lib/client';
	import { createClient } from '$lib/client/client';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { toast } from 'svelte-sonner';
	import { Button } from './ui/button';
	import Input from './ui/input/input.svelte';
	import { invalidatePages } from '$lib/utilities/storage';
	import { page } from '$app/state';

	let {
		open = $bindable(),
		item
	}: {
		open: boolean;
		item: FileFolderPublic;
	} = $props();

	const client = createClient({ baseUrl: '' });

	let newName = $derived(item.name);

	async function saveRename() {
		if (newName.trim() === item.name) {
			open = false;
			return;
		}
		if (!newName.trim()) {
			toast.error('Name cannot be empty');
			return;
		}

		if (item.type === 'directory') {
			const { data } = await storageRenameFolderFolderIdPatch({
				client,
				path: { folder_id: item.id },
				query: { folder_name: newName },
				throwOnError: true
			});
			toast.success(data);
		} else {
			const { data } = await storageRenameFileFileIdPatch({
				client,
				path: { file_id: item.id },
				query: { file_name: newName },
				throwOnError: true
			});
			toast.success(data);
		}
		invalidatePages(page.url.pathname);
		open = false;
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="w-105" showCloseButton={false}>
		<Dialog.Header class="space-y-3">
			<Dialog.Title class="text-lg font-semibold">
				Rename {item.type === 'directory' ? 'folder' : 'file'}
			</Dialog.Title>
		</Dialog.Header>

		<div class="mt-2 flex flex-col gap-3">
			<Input
				type="text"
				bind:value={newName}
				class="w-full rounded border px-3 py-2 text-sm"
				placeholder="Enter new name"
			/>
			<div class="mt-3 flex justify-end gap-2">
				<Button variant="outline" onclick={() => (open = false)} class="cursor-pointer"
					>Cancel</Button
				>
				<Button onclick={saveRename} class="cursor-pointer">Save</Button>
			</div>
		</div>
	</Dialog.Content>
</Dialog.Root>
