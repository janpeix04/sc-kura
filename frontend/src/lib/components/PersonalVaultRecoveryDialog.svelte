<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Form from '$lib/components/ui/form';
	import { m } from '$lib/paraglide/messages';
	import { toast } from 'svelte-sonner';
	import { Button } from './ui/button';
	import { Input } from './ui/input';
	import { resetPasswordSchema, type ResetVaultPasswordSchema } from '$lib/schemas/auth';
	import { superForm, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { clientSideClient } from '$lib/utilities/client-side';
	import { cryptoUsersKeysGet } from '$lib/client';
	import {
		arrayBufferToBase64,
		base64ToArrayBuffer,
		decryptPrivateKey,
		deriveKeyFromPassword,
		encryptPrivateKey,
		exportKey,
		getRandomValues,
		importKey
	} from '$lib/crypto';
	import { privateKey, publicKey } from '$lib/stores/crypto';
	import { get } from 'svelte/store';

	let {
		open = $bindable(),
		resetPasswordForm
	}: {
		open: boolean;
		resetPasswordForm: SuperValidated<ResetVaultPasswordSchema>;
	} = $props();

	const form = superForm(resetPasswordForm, {
		validators: zod4Client(resetPasswordSchema),
		dataType: 'json'
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

			const privateKeyBuffer = await decryptPrivateKey(recovery, iv, encryptedPrivateKey);
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
			<form
				action="?/resetPassword"
				method="POST"
				class="flex w-full max-w-xl flex-col gap-2"
				use:enhance={{
					async onSubmit({ cancel }) {
						const priv = get(privateKey);

						if (!priv || !recoveryKey) {
							cancel();
							return;
						}

						const privateKeyBuffer = await exportKey('pkcs8', priv);
						const salt = getRandomValues(16);
						const passwordKey = await deriveKeyFromPassword($formData.password, salt);
						const { iv, encrypted } = await encryptPrivateKey(passwordKey, privateKeyBuffer);

						$formData.salt = arrayBufferToBase64(salt);
						$formData.iv = arrayBufferToBase64(iv);
						$formData.encryptedPrivateKey = arrayBufferToBase64(encrypted);
					},
					onResult({ result }) {
						if (result.type === 'failure') {
							const form = result.data?.form;

							if (form.message) {
								toast.error(form.message);
							}
						}

						if (result.type === 'success') {
							toast.success(m.password_updated_successfully());
							open = false;
						}
					}
				}}
			>
				<h2 class="text-lg font-semibold">{m.reset_password()}</h2>

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
								required
							/>
						{/snippet}
					</Form.Control>
					<Form.FieldErrors />
				</Form.Field>

				<Form.Field {form} name="confirmPassword">
					<Form.Control>
						{#snippet children({ props })}
							<Form.Label>{m.password()}</Form.Label>
							<Input
								{...props}
								type="password"
								placeholder="••••••••"
								autocomplete="new-password"
								bind:value={$formData.confirmPassword}
								required
							/>
						{/snippet}
					</Form.Control>
					<Form.FieldErrors />
				</Form.Field>

				<div class="flex justify-end">
					<Form.Button type="submit">{m.confirm()}</Form.Button>
				</div>
			</form>
		{/if}
	</Dialog.Content>
</Dialog.Root>
