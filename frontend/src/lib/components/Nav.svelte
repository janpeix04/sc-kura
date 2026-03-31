<script lang="ts">
	import type { UserPublic } from '$lib/client';
	import * as Avatar from '$lib/components/ui/avatar/index.js';
	import { getUserInitials } from '$lib/utilities/utils.js';

	let { user }: { user: UserPublic } = $props();
</script>

<header class="flex shrink-0 items-center justify-between gap-2 p-2">
	<div class="ml-3 w-72 flex items-center">
        <img src="/logo.svg" alt="Kura logo" class="w-16">
        <h1 class="text-xl font-medium">Kura</h1>
    </div>

	<div class="h-12 w-full px-10">
		<form class="flex items-center gap-2 rounded-full bg-search-background p-1.5">
			<span class="ml-4 icon-[lucide--search] size-6"></span>
			<input
				class="w-full border-none bg-search-background outline-none"
				type="text"
				placeholder="Search in Kura"
			/>
		</form>
	</div>

	<div class="mr-3">
		<Avatar.Root class="size-10">
			<Avatar.Image src="" alt="logo" />
			<Avatar.Fallback class="bg-search-background">
				{getUserInitials(user.first_name, user.last_name)}
			</Avatar.Fallback>
		</Avatar.Root>
	</div>
</header>
