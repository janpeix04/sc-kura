<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog/index';
	import { m } from '$lib/paraglide/messages';
	import { emptyTrash } from '$lib/utilities/delete';
	import { invalidatePage } from '$lib/utilities/utils';
	import Button from './ui/button/button.svelte';

	let {
		isOpen = $bindable(),
		title,
		description,
		confirm
	}: {
		isOpen: boolean;
		title: string;
		description: string;
		confirm: string;
	} = $props();
</script>

<Dialog.Root bind:open={isOpen}>
	<Dialog.Content class="min-w-140">
		<Dialog.Header>
			<Dialog.Title>{title}</Dialog.Title>
			<Dialog.Description>{description}</Dialog.Description>
		</Dialog.Header>

		<div class="flex justify-end gap-2">
			<Button
				type="button"
				variant="outline"
				onclick={() => {
					isOpen = false;
				}}
			>
				{m.cancel()}
			</Button>
			<Button
				type="submit"
				variant="delete"
				onclick={() => {
					emptyTrash().finally(invalidatePage);
					isOpen = false;
				}}
			>
				{confirm}
			</Button>
		</div>
	</Dialog.Content>
</Dialog.Root>
