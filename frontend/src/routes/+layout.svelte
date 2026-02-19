<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { Toaster } from '$lib/components/ui/sonner/index';
	import Header from '$lib/components/Header.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';

	let { children } = $props();
</script>

<Toaster position="top-center" richColors closeButton />
<Header />
<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="flex h-screen w-full flex-col overflow-hidden">
	<Sidebar.Provider>
		<Sidebar.Inset>
			<main class="flex-1">
				{@render children()}
			</main>
		</Sidebar.Inset>
	</Sidebar.Provider>
</div>
