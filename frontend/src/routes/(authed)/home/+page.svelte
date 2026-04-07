<script lang="ts">
	import StorageLayout from "$lib/layouts/StorageLayout.svelte";
	import type { CreateFolderSchema } from "$lib/schemas/storage.js";
	import { setContext } from "svelte";
	import type { SuperValidated } from "sveltekit-superforms";

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
</script>

{#snippet children()}
	test
{/snippet}

<StorageLayout user={data.user} {children} />
