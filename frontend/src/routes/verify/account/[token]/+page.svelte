<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	let { data } = $props();
</script>

<div class="bg-primary flex h-full w-full items-center justify-center">
	<div class="bg-secondary w-105 rounded-3xl px-10 py-6">
		<div class="mb-8 text-center">
			<h2 class="text-xl font-semibold">Account Verification</h2>
		</div>
		<div>
			{#if data.success}
				<p>{data.success}</p>
				<Button href="/login" class="mt-4 h-11 w-full px-2.5">Proceed to Log in</Button>
			{:else}
				<p>{data.error}</p>
			{/if}
		</div>
	</div>
</div>
