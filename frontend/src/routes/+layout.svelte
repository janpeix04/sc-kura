<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { Toaster } from '$lib/components/ui/sonner';

	let { children } = $props();
</script>

<Toaster position="top-center" richColors closeButton />
<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<div class="flex h-screen flex-col">
	<main>
		{@render children()}
	</main>
</div>
