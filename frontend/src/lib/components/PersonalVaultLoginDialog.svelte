<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Form from '$lib/components/ui/form';
	import Input from './ui/input/input.svelte';

	let {
		open = $bindable()
	}: {
		open: boolean;
	} = $props();
</script>

<Dialog.Root bind:open>
	<Dialog.Content
		showCloseButton={false}
		onInteractOutside={(e) => e.preventDefault()}
		onEscapeKeydown={(e) => e.preventDefault()}
	>
		<form action="">
			<Form.Field>
				<Form.Control>
					{#snippet children({ props })}
						<Input
							type="password"
							placeholder="••••••••"
							autocomplete="new-password"
							bind:value={password}
							required
						/>
					{/snippet}
				</Form.Control>
			</Form.Field>
		</form>
	</Dialog.Content>
</Dialog.Root>
