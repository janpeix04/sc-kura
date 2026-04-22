<script lang="ts">
	import { verifyPasswordPost } from '$lib/client';
	import * as Dialog from '$lib/components/ui/dialog';
	import { m } from '$lib/paraglide/messages';
	import { Button } from './ui/button';
	import { Input } from './ui/input';
	import { clientSideClient } from '$lib/utilities/client-side';
	import { toast } from 'svelte-sonner';

	let {
		open = $bindable()
	}: {
		open: boolean;
	} = $props();

	let password: string = $state('');
	let recoveryKey: string = $state('ABCD-EFGH-IJKL-MNOP-QRSTU-VWXY');
	let step: number = $state(1);

	function nextStep() {
		step += 1;
	}

	async function verifyPassword(password: string) {
		const { data } = await verifyPasswordPost({
			client: clientSideClient,
			query: {
				password
			},
			throwOnError: true
		});

		return data;
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content>
		{#if step === 1}
			<h2 class="text-lg font-semibold">{m.welcome_to_your_personal_vault()}</h2>

			<p class="text-sm text-muted-foreground">
				{m.personal_vault_intro()}
			</p>

			<p class="text-sm text-muted-foreground">
				{m.personal_vault_privacy_notice()}
			</p>

			<p class="text-sm text-muted-foreground">
				{m.personal_vault_setup_notice()}
			</p>

			<div class="mt-6 flex justify-end">
				<Button type="button" variant="default" onclick={nextStep}>{m.continue()}</Button>
			</div>
		{:else if step === 2}
			<h2 class="text-lg font-semibold">{m.confirm_your_password()}</h2>

			<p class="text-sm text-muted-foreground">
				{m.confirm_your_password_description()}
			</p>

			<Input
				type="password"
				placeholder="••••••••"
				autocomplete="new-password"
				bind:value={password}
				required
			/>

			<div class="flex justify-end">
				<Button
					type="button"
					variant="default"
					disabled={!password}
					onclick={async () => {
						const correct = await verifyPassword(password);

						if (!correct) {
							toast.error(m.incorrect_password());
							return;
						}

						nextStep();
					}}
				>
					{m.continue()}
				</Button>
			</div>
		{:else if step === 3}
			<h2 class="text-lg font-semibold">{m.account_recovery()}</h2>

			<div class="flex flex-col items-center justify-center gap-2">
				<span class="icon-[lucide--key-round] size-8"></span>
				<p class="text-base text-muted-foreground">{m.here_is_your_recovery_key()}</p>
			</div>

			<p class="text-sm text-muted-foreground">
				{m.recovery_key_description()}
			</p>

			<p class="text-sm text-muted-foreground">
				{m.recovery_key_warning()} <strong>{m.recovery_key_warning_strong()}</strong>
			</p>

			<div class="flex flex-col gap-2">
				<span class="font-bold">{m.backup_your_recovery_key()}</span>

				<Button type="button" variant="ghost" class="flex justify-start">
					<span class="icon-[lucide--key-round] size-4"></span>
					<span>{recoveryKey}</span>
				</Button>

				<Button>{m.download_key()}</Button>
			</div>
		{/if}
	</Dialog.Content>
</Dialog.Root>
