<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Form from '$lib/components/ui/form';
	import { m } from '$lib/paraglide/messages';
	import { toast } from 'svelte-sonner';
	import { Button } from './ui/button';
	import { Input } from './ui/input';
	import { resetPasswordSchema, type ResetPasswordSchema } from '$lib/schemas/auth';
	import { superForm, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { clientSideClient } from '$lib/utilities/client-side';
	import { cryptoUsersKeysGet } from '$lib/client';
	import { base64ToArrayBuffer, decryptPrivateKey, importKey } from '$lib/crypto';
	import { privateKey, publicKey } from '$lib/stores/crypto';

	let {
		open = $bindable(),
		resetPasswordForm
	}: {
		open: boolean;
		resetPasswordForm: SuperValidated<ResetPasswordSchema>;
	} = $props();

	const form = superForm(resetPasswordForm, {
		validators: zod4Client(resetPasswordSchema)
	});

	const { form: formData, enhance } = form;

	let step: number = $state(1);
	let recoveryKey: string | undefined = $state();

	function nextStep() {
		step += 1;
	}

	async function getUserKeys() {
		const { data, error } = await cryptoUsersKeysGet({
			client: clientSideClient
		});

		if (error) {
			toast.error(m.oops_something_went_wrong());
			return;
		}

		return data;
	}

	async function verifyRecoveryKey() {
		if (!recoveryKey) {
			toast.error(m.oops_something_went_wrong());
			return;
		}
		const keys = await getUserKeys();

		if (!keys) return;

		try {
			const publicKeyBuffer = base64ToArrayBuffer(keys.public_key);
			const pub = await importKey(
				'spki',
				publicKeyBuffer,
				{ name: 'RSA-OAEP', hash: 'SHA-512' },
				true,
				['wrapKey']
			);

			const encryptedPrivateKey = base64ToArrayBuffer(keys.encrypted_private_key_recovery);
			const iv = base64ToArrayBuffer(keys.iv_recovery);
			const recovery = await importKey(
				'raw',
				base64ToArrayBuffer(recoveryKey),
				{ name: 'AES-GCM' },
				false,
				['encrypt', 'decrypt']
			);

			console.log(recoveryKey);

			const privateKeyBuffer = await decryptPrivateKey(recovery, iv, encryptedPrivateKey);
			console.log(privateKeyBuffer);
			const priv = await importKey(
				'pkcs8',
				privateKeyBuffer,
				{ name: 'RSA-OAEP', hash: 'SHA-512' },
				true,
				['unwrapKey']
			);

			privateKey.set(priv);
			publicKey.set(pub);

			if (privateKeyBuffer) return true;

			return false;
		} catch {
			toast.error(m.oops_something_went_wrong());
			return false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content
		class="flex w-full max-w-xl flex-col gap-2"
		showCloseButton={false}
		onEscapeKeydown={(e) => e.preventDefault()}
		onInteractOutside={(e) => e.preventDefault()}
	>
		{#if step === 1}
			<h2 class="text-lg font-semibold">{m.recovery_key()}</h2>

			<p class="text-sm text-muted-foreground">
				{m.provide_recovery_key()}
			</p>

			<Input type="text" placeholder={m.recovery_key()} bind:value={recoveryKey} required />

			<div class="flex justify-end">
				<Button
					type="button"
					variant="default"
					disabled={!recoveryKey}
					onclick={async () => {
						const isVerify = await verifyRecoveryKey();
						if (isVerify) nextStep();
					}}
				>
					{m.verify()}
				</Button>
			</div>
		{:else if step === 2}
			<form action="?/resetPassword" method="POST" use:enhance>
				<h2 class="text-lg font-semibold">{m.reset_password()}</h2>

				<p class="text-sm text-muted-foreground">new password description</p>

				<Form.Field {form} name="password">
					<Form.Control>
						{#snippet children({ props })}
							<Form.Label>{m.password()}</Form.Label>
							<Input
								{...props}
								type="password"
								placeholder="••••••••"
								autocomplete="new-password"
								bind:value={$formData.password}
							/>
						{/snippet}
					</Form.Control>
				</Form.Field>

				<Form.Field {form} name="password">
					<Form.Control>
						{#snippet children({ props })}
							<Form.Label>{m.confirm_password()}</Form.Label>
							<Input
								{...props}
								type="password"
								placeholder="••••••••"
								autocomplete="new-password"
								bind:value={$formData.confirmPassword}
							/>
						{/snippet}
					</Form.Control>
					<Form.FieldErrors />
				</Form.Field>

				<div class="flex justify-end">
					<Button
						type="button"
						variant="default"
						disabled={!recoveryKey}
						onclick={async () => {
							nextStep();
						}}
					>
						{m.verify()}
					</Button>
				</div>
			</form>
		{/if}
	</Dialog.Content>
</Dialog.Root>
