<script lang="ts">
	import { page } from '$app/state';
	import { Button } from './ui/button';

	let isLoginPage = $derived(page.url.pathname.startsWith('/login'));
	let isStoragePage = $derived(page.url.pathname.startsWith('/storage') || page.url.pathname.startsWith('/calendar'));
</script>

{#if !isStoragePage}
	<nav
		class="bg-primary fixed top-0 left-0 z-50 flex h-22.5 w-full items-center justify-between px-10"
	>
		<h1 class="text-secondary text-2xl font-bold">Kura</h1>
		<Button
			href={isLoginPage ? '/signup' : '/login'}
			class="bg-primary-high hover:bg-primary-high2 font-semibold"
			>{isLoginPage ? 'SIGN UP FREE' : 'Login'}</Button
		>
	</nav>
{/if}
