<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from './ui/button';

	let {
		deleteDialogOpen = $bindable(),
		onClick
	}: {
		deleteDialogOpen: boolean;
		onClick: () => void;
	} = $props();
</script>

<Dialog.Root bind:open={deleteDialogOpen}>
	<Dialog.Content showCloseButton={false}>
		<Dialog.Header>
			<Dialog.Title>Delete forever?</Dialog.Title>
		</Dialog.Header>
		All items in bin will be deleted forever. This can't be undone.
		<div class="flex justify-end gap-2">
			<Button variant="outline" onclick={() => deleteDialogOpen = false}>Cancel</Button>
			<Button class="bg-semantic-error text-white hover:bg-red-400 cursor-pointer" onclick={onClick}>Delete</Button>
		</div>
	</Dialog.Content>
</Dialog.Root>
