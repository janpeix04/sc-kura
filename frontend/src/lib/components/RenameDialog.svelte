<script lang="ts">
	import type { FilePublic, FolderPublic } from '$lib/client';
	/* import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { m } from '$lib/paraglide/messages';
	import { renameItem } from '$lib/utilities/rename';
	import { invalidatePage } from '$lib/utilities/utils';
	import Button from './ui/button/button.svelte'; */
	let {
		open = $bindable(),
		item
	}: {
		open: boolean;
		item: FolderPublic | FilePublic;
	} = $props();

	let newName = $state<string>(item.name);
	console.log(newName);
</script>

<!-- <Dialog.Root bind:open>
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
					renameItem(item, newName).finally(invalidatePage);
					open = false;
				}}
				disabled={newName === ''}
			>
				{m.save()}
			</Button>
		</div>
	</Dialog.Content>
</Dialog.Root>
 -->
