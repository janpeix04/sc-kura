<script lang="ts">
	import type { CryptoBreadcrumbs } from '$lib/client';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import type { DecryptedBreadcrumb } from '$lib/schemas/types';

	let { breadcrumbs }: { breadcrumbs: DecryptedBreadcrumb[] } = $props();

	const hasHidden = $derived(breadcrumbs.length >= 3);

	const hidden = $derived(hasHidden ? breadcrumbs.slice(0, breadcrumbs.length - 2) : []);

	const visible = $derived(hasHidden ? breadcrumbs.slice(-2) : breadcrumbs);
</script>

<Breadcrumb.Root>
	<Breadcrumb.List class="text-lg">
		{#if !hasHidden}
			<Breadcrumb.Item>
				<Breadcrumb.Link href={localizeHref('/personal-vault')}>
					<span class="text-2xl">{m.personal_vault()}</span>
				</Breadcrumb.Link>
			</Breadcrumb.Item>
		{/if}

		{#if hidden.length}
			<DropdownMenu.Root>
				<DropdownMenu.Trigger
					class="flex cursor-pointer items-center justify-center hover:text-foreground"
				>
					<span class="icon-[lucide--ellipsis] size-6"></span>
				</DropdownMenu.Trigger>

				<DropdownMenu.Content class="w-fit">
					<DropdownMenu.Item class="cursor-pointer">
						<a href={localizeHref('/personal-vault')} class="flex w-full items-center gap-2">
							<span class="icon-[lucide--hard-drive] size-4"></span>
							{m.personal_vault()}
						</a>
					</DropdownMenu.Item>
					{#each hidden as el (el.folder_id)}
						<DropdownMenu.Item class="cursor-pointer">
							<a href={localizeHref(`/personal-vault/folder/${el.folder_id}`)}>
								{el.name}
							</a>
						</DropdownMenu.Item>
					{/each}
				</DropdownMenu.Content>
			</DropdownMenu.Root>
		{/if}

		{#each visible as breadcrumb (breadcrumb.folder_id)}
			<Breadcrumb.Separator class="flex" />
			<Breadcrumb.Item>
				<Breadcrumb.Link href={localizeHref(`/personal-vault/folder/${breadcrumb.folder_id}`)}>
					<span class="text-2xl">{breadcrumb.name}</span>
				</Breadcrumb.Link>
			</Breadcrumb.Item>
		{/each}
	</Breadcrumb.List>
</Breadcrumb.Root>
