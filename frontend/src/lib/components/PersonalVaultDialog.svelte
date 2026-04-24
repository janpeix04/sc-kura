<script lang="ts">
	import { cryptoUserKeysPost, verifyPasswordPost, type UserPublic } from '$lib/client';
	import * as Dialog from '$lib/components/ui/dialog';
	import { m } from '$lib/paraglide/messages';
	import { Button } from './ui/button';
	import { Input } from './ui/input';
	import { clientSideClient } from '$lib/utilities/client-side';
	import { toast } from 'svelte-sonner';
	import { downloadBlob } from '$lib/utilities/download';
	import {
		arrayBufferToBase64,
		base64ToArrayBuffer,
		deriveKeyFromPassword,
		encryptPrivateKey,
		exportKey,
		generateRecoveryKey,
		generateRSAKeyPair,
		getRandomValues,
		importKey
	} from '$lib/e2ee';
	import { superForm, type SuperValidated } from 'sveltekit-superforms';
	import { updateUserSchema, type UpdateUserSchema } from '$lib/schemas/user';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { privateKey, publicKey } from '$lib/stores/crypto';

	let {
		open = $bindable(),
		user,
		updateUserForm
	}: {
		open: boolean;
		user: UserPublic;
		updateUserForm: SuperValidated<UpdateUserSchema>;
	} = $props();

	const updateForm = superForm(updateUserForm, {
		validators: zod4Client(updateUserSchema)
	});

	const { enhance } = updateForm;

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

	function copyRecoveryKey() {
		navigator.clipboard.writeText(recoveryKey);
		toast.info(m.recovery_key_copied_to_clipboard());
	}

	function downloadRecoveryKey() {
		const blob = new Blob([recoveryKey], { type: 'text/plain' });
		downloadBlob(blob, 'KURA-RECOVERYKEY.txt');
	}

	async function generateKeys() {
		const rsa = await generateRSAKeyPair();

		const privateKeyBuffer = await exportKey('pkcs8', rsa.privateKey);
		const publicKeyBuffer = await exportKey('spki', rsa.publicKey);

		publicKey.set(rsa.publicKey);
		privateKey.set(rsa.privateKey);

		const recoveryKeyBase64 = generateRecoveryKey();
		const recoveryKeyRaw = base64ToArrayBuffer(recoveryKeyBase64);

		const recovery = await importKey('raw', recoveryKeyRaw, { name: 'AES-GCM' }, false, [
			'encrypt',
			'decrypt'
		]);

		recoveryKey = recoveryKeyBase64;

		const salt = getRandomValues(16);
		const passwordKey = await deriveKeyFromPassword(password, salt);

		const { iv, encrypted: encryptedPrivateKey } = await encryptPrivateKey(
			passwordKey,
			privateKeyBuffer
		);

		const { iv: ivRecovery, encrypted: encryptedPrivateKeyRecovery } = await encryptPrivateKey(
			recovery,
			privateKeyBuffer
		);

		await cryptoUserKeysPost({
			client: clientSideClient,
			body: {
				user_id: user.id,
				public_key: arrayBufferToBase64(publicKeyBuffer),
				encrypted_private_key: arrayBufferToBase64(encryptedPrivateKey),
				encrypted_private_key_recovery: arrayBufferToBase64(encryptedPrivateKeyRecovery),
				iv: arrayBufferToBase64(iv),
				iv_recovery: arrayBufferToBase64(ivRecovery),
				pbkdf2_salt: arrayBufferToBase64(salt)
			}
		});
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
						generateKeys();
						nextStep();
					}}
				>
					{m.continue()}
				</Button>
			</div>
		{:else if step === 3}
			<form
				class="flex w-full flex-1 flex-col gap-2"
				action="?/markHasSeenPersonalVault"
				method="POST"
				use:enhance={{
					onSubmit({ formData }) {
						formData.set('hasSeenPersonalVault', 'true');
					},
					onResult({ result }) {
						if (result.type === 'success') {
							open = false;
						}
					}
				}}
			>
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

					<Button
						type="button"
						variant="ghost"
						class="flex w-full justify-start"
						onclick={copyRecoveryKey}
					>
						<span class="icon-[lucide--key-round] size-4"></span>
						<span>{recoveryKey}</span>
					</Button>

					<Button onclick={downloadRecoveryKey}>{m.download_key()}</Button>

					<Button type="submit" variant="outline">{m.close()}</Button>
				</div>
			</form>
		{/if}
	</Dialog.Content>
</Dialog.Root>
