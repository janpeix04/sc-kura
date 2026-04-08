<script lang="ts">
	import type { UserPublic } from '$lib/client';
	import * as Avatar from '$lib/components/ui/avatar/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import { capitalize, getUserInitials } from '$lib/utilities/utils.js';
	import { locales, localizeHref, setLocale } from '$lib/paraglide/runtime';
	import { m } from '$lib/paraglide/messages';

	let { user }: { user: UserPublic } = $props();

	const languages = {
		en: 'English',
		es: 'Español',
		ca: 'Català'
	};
</script>

<header class="flex shrink-0 items-center justify-between gap-2 p-2">
	<div class="flex w-72 items-center">
		<a class="flex items-center" href={localizeHref('/home')}>
			<img src="/logo.svg" alt="Kura logo" class="w-16" />
			<h1 class="text-xl font-medium">Kura</h1>
		</a>
	</div>

	<div class="h-12 w-full px-12">
		<form
			class="flex items-center gap-2 rounded-full bg-search-background p-1 transition-colors duration-300 ease-in-out focus-within:bg-white focus-within:shadow-sm"
		>
			<span class="ml-4 icon-[lucide--search] size-6"></span>
			<input
				class="w-full border-none bg-transparent outline-none focus:ring-0 focus:outline-none focus-visible:ring-0"
				type="text"
				placeholder={m.search_in_kura()}
			/>
		</form>
	</div>

	<div class="mr-3">
		<DropdownMenu.Root>
			<DropdownMenu.Trigger class="cursor-pointer">
				<Avatar.Root class="size-10">
					<Avatar.Image src="" alt="logo" />
					<Avatar.Fallback class="bg-search-background">
						{getUserInitials(user.first_name, user.last_name)}
					</Avatar.Fallback>
				</Avatar.Root>
			</DropdownMenu.Trigger>
			<DropdownMenu.Content align="end" class="w-fit">
				<DropdownMenu.Group>
					<DropdownMenu.Sub>
						<DropdownMenu.SubTrigger openDelay={400}>{m.language()}</DropdownMenu.SubTrigger>
						<DropdownMenu.SubContent align="end" side="bottom" class="z-50">
							{#each locales as locale (locale)}
								<DropdownMenu.Item class="cursor-pointer" onclick={() => setLocale(locale)}
									>{languages[locale]}</DropdownMenu.Item
								>
							{/each}
						</DropdownMenu.SubContent>
					</DropdownMenu.Sub>
				</DropdownMenu.Group>
				<DropdownMenu.Item class="cursor-pointer">
					<a href={localizeHref('/logout')} class="flex items-center gap-2">
						{m.logout()} <span class="icon-[lucide--log-out] size-4"></span>
					</a>
				</DropdownMenu.Item>
			</DropdownMenu.Content>
		</DropdownMenu.Root>
	</div>
</header>
