<script lang="ts">
	import type { FilePublic, FolderPublic } from '$lib/client';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Form from '$lib/components/ui/form/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { m } from '$lib/paraglide/messages';
	import { renameItemSchema, type RenameItemSchema } from '$lib/schemas/storage';
	import { superFormOnResult } from '$lib/utilities/actions';
	import { getContext } from 'svelte';
	import { superForm, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';

	let {
		open = $bindable(),
		item
	}: {
		open: boolean;
		item: FolderPublic | FilePublic;
	} = $props();

	let newName = $state<string>(item.name);

	const renameFolderForm = getContext<SuperValidated<RenameItemSchema>>('renameItemForm');

	const form = superForm(renameFolderForm, {
		validators: zod4Client(renameItemSchema)
	});

	const { enhance } = form;
</script>

<Dialog.Root bind:open>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>{m.rename()}</Dialog.Title>
		</Dialog.Header>
		<form
			class="flex flex-col gap-2"
			action="?/renameFolder"
			method="POST"
			use:enhance={{
				onSubmit({ formData }) {
					formData.set('name', newName);
					formData.set('itemId', item.id);
				},
				onResult: superFormOnResult
			}}
		>
			<Form.Field {form} name="name">
				<Form.Control>
					{#snippet children({ props })}
						<Input
							type="text"
							{...props}
							bind:value={newName}
							onfocus={(e) => e.currentTarget.select()}
							autofocus
						/>
					{/snippet}
				</Form.Control>
			</Form.Field>

			<div class="flex justify-end gap-2">
				<Form.Button
					type="button"
					variant="outline"
					onclick={() => {
						form.reset();
						open = false;
					}}
				>
					{m.cancel()}
				</Form.Button>
				<Form.Button type="submit" onclick={() => (open = false)} disabled={newName === ''}>
					{m.save()}
				</Form.Button>
			</div>
		</form>
	</Dialog.Content>
</Dialog.Root>
