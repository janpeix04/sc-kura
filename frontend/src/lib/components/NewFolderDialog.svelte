<script lang="ts">
	let {
		open = $bindable()
	}: {
		open: boolean;
	} = $props();
</script>

<!-- <Dialog.Root bind:open>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>{m.new_folder()}</Dialog.Title>
		</Dialog.Header>
		<form
			class="flex flex-col gap-2"
			action="?/createFolder"
			method="POST"
			use:enhance={{
				onSubmit({ formData }) {
					const name = formData.get('name');
					if (name === '') {
						formData.set('name', m.new_folder());
					}
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
							bind:value={$formData.name}
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
				<Form.Button type="submit" onclick={() => (open = false)}>{m.create()}</Form.Button>
			</div> 
		</form>
	</Dialog.Content>
</Dialog.Root> -->
