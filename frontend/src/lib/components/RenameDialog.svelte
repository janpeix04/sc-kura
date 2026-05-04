<script lang="ts">
	import { page } from '$app/state';
	import type { FilePublic, FolderPublic } from '$lib/client';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { m } from '$lib/paraglide/messages';
	import type { DecryptedFolder } from '$lib/schemas/types';
	import { renameItem } from '$lib/utilities/rename';
	import { invalidatePage } from '$lib/utilities/utils';
	import Button from './ui/button/button.svelte';
	let {
		open = $bindable(),
		item,
		isEncrypted = false
	}: {
		open: boolean;
		item: FolderPublic | FilePublic | DecryptedFolder;
		isEncrypted?: boolean;
	} = $props();

	let newName = $state<string>(item.name);
</script>

<Dialog.Root bind:open>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>{m.rename()}</Dialog.Title>
		</Dialog.Header>

		<Input type="text" bind:value={newName} onfocus={(e) => e.currentTarget.select()} autofocus />

		<div class="flex justify-end gap-2">
			<Button
				type="button"
				variant="outline"
				onclick={() => {
					open = false;
				}}
			>
				{m.cancel()}
			</Button>
			<Button
				type="submit"
				onclick={() => {
					renameItem(item, newName, isEncrypted).finally(invalidatePage);
					open = false;
				}}
				disabled={newName === ''}
			>
				{m.save()}
			</Button>
		</div>
	</Dialog.Content>
</Dialog.Root>
