<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';

	let { data } = $props();
</script>

<div class="flex min-h-screen items-center justify-center bg-gray-50 px-4">
	<div class="w-full max-w-md rounded-2xl border bg-white p-8 text-center shadow-lg">
		{#if data.success}
			<div class="space-y-4">
				<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
					<span class="icon-[lucide--badge-check] size-12 text-green-600"></span>
				</div>

				<h1 class="text-2xl font-semibold text-gray-900">{m.account_verified()}</h1>

				<p class="text-sm text-gray-600">
					{data.success}
				</p>
			</div>
		{:else}
			<div class="space-y-4">
				<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
					<span class="icon-[lucide--badge-check] size-12 text-red-600"></span>
				</div>

				<h1 class="text-2xl font-semibold text-gray-900">{m.verification_failed()}</h1>

				<p class="text-sm text-gray-600">
					{data.error}
				</p>
			</div>
		{/if}
		<div class="mt-6">
			<a
				href={localizeHref('/login')}
				class="inline-block w-full rounded-lg bg-black px-4 py-2 text-white transition hover:bg-gray-800"
			>
				{m.go_to_login()}
			</a>
		</div>
	</div>
</div>
