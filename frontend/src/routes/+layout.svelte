<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { Toaster } from '$lib/components/ui/sonner/index';
	import Header from '$lib/components/Header.svelte';

	let { children } = $props();
</script>

<Toaster position="top-center" richColors closeButton />
<Header />
<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="flex h-screen w-full flex-col overflow-hidden">
	<main class="flex-1">
		{@render children()}
	</main>
</div>
