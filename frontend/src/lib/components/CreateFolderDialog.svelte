<script lang="ts">
	import { enhance } from '$app/forms';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import Button from './ui/button/button.svelte';
	import { currentStoragePath } from '$lib/stores/storage';
	import { Input } from './ui/input';

	let { dialogOpen = $bindable() }: { dialogOpen: boolean } = $props();

	let folderName: string | undefined = $state();

	function reset() {
		folderName = undefined;
		dialogOpen = false;
	}
</script>

<Dialog.Root bind:open={dialogOpen}>
	<Dialog.Content showCloseButton={false}>
		<Dialog.Header>
			<Dialog.Title class="text-center">Create folder</Dialog.Title>
		</Dialog.Header>
		<form
			action="?/createFolder"
			method="POST"
			enctype="multipart/form-data"
			class="flex flex-col gap-4"
			use:enhance={({ formData, cancel }) => {
				if (!folderName || !folderName.trim()) {
					cancel();
					return;
				}
				formData.set('folder_name', folderName);
				formData.set('path', $currentStoragePath);
				reset();
			}}
		>
			<Input type="text" placeholder="Folder name" bind:value={folderName} />
			<div class="flex justify-end gap-2">
				<Button variant="outline" onclick={reset}>Cancel</Button>
				<Button type="submit" disabled={folderName === undefined}>Create</Button>
			</div>
		</form>
	</Dialog.Content>
</Dialog.Root>
