<script lang="ts">
	import PersonalVaultDialog from '$lib/components/PersonalVaultDialog.svelte';
	import PersonalVaultLoginDialog from '$lib/components/PersonalVaultLoginDialog.svelte';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { vault } from '$lib/stores/vault';
	import { onMount, setContext } from 'svelte';

	let { data } = $props();

	let showFirstTime = $state(false);

	setContext('createFolderForm', data.createFolderForm);

	onMount(() => {
		if (!data.hasSeen) {
			showFirstTime = true;
			$vault.locked = true;
			return;
		}

		if (data.hasSeen && !$vault.token) {
			$vault.locked = true;
		}
	});

	$effect(() => {
		$effect(() => {
			'called';
		});
		const expiresAt = $vault.expiresAt;

		if (!expiresAt) return;

		const remaining = expiresAt - Date.now();

		if (remaining <= 0) {
			$vault.locked = true;
			$vault.token = null;
			$vault.expiresAt = null;
			return;
		}

		const timer = setTimeout(() => {
			$vault.locked = true;
			$vault.token = null;
			$vault.expiresAt = null;
		}, remaining);

		return () => clearTimeout(timer);
	});
</script>

{#if showFirstTime}
	<PersonalVaultDialog open={showFirstTime} user={data.user} updateUserForm={data.updateUserForm} />
{:else if $vault.locked}
	<PersonalVaultLoginDialog open={!showFirstTime} verifyPasswordForm={data.verifyPasswordForm} />
{/if}

<StorageLayout user={data.user} folderId={data.folderId} availableSpace={data.availableSpace}>
	dsasd
</StorageLayout>
