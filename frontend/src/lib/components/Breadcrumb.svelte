<script lang="ts">
	import type { Breadcrumbs } from '$lib/client';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';

	let { breadcrumbs }: { breadcrumbs: Breadcrumbs[] } = $props();

	const hasHidden = $derived(breadcrumbs.length >= 3);

	const hidden = $derived(hasHidden ? breadcrumbs.slice(0, breadcrumbs.length - 2) : []);

	const visible = $derived(hasHidden ? breadcrumbs.slice(-2) : breadcrumbs);
</script>

<Breadcrumb.Root>
	<Breadcrumb.List class="text-lg">
		{#if !hasHidden}
			<Breadcrumb.Item>
				<Breadcrumb.Link href={localizeHref('/my-files')}>
					<span class="text-2xl">{m.my_files()}</span>
				</Breadcrumb.Link>
			</Breadcrumb.Item>
		{/if}

		{#if hidden.length}
			<!-- <DropdownMenu.Root>
				<DropdownMenu.Trigger
					class="flex cursor-pointer items-center justify-center hover:text-foreground"
				>
					<span class="icon-[lucide--ellipsis] size-6"></span>
				</DropdownMenu.Trigger>

				<DropdownMenu.Content>
					<DropdownMenu.Item class="cursor-pointer">
						<a href={localizeHref('/my-files')} class="flex items-center gap-2 w-full">
							<span class="icon-[lucide--hard-drive] size-4"></span>
							{m.my_files()}
						</a>
					</DropdownMenu.Item>
					{#each hidden as el (el.folder_id)}
						<DropdownMenu.Item class="cursor-pointer">
							<a href={localizeHref(`/folder/${el.folder_id}`)}>
								{el.folder_name}
							</a>
						</DropdownMenu.Item>
					{/each}
				</DropdownMenu.Content>
			</DropdownMenu.Root> -->
		{/if}

		{#each visible as breadcrumb (breadcrumb.folder_id)}
			<Breadcrumb.Separator class="flex" />
			<Breadcrumb.Item>
				<Breadcrumb.Link href={localizeHref(`/folder/${breadcrumb.folder_id}`)}>
					<span class="text-2xl">{breadcrumb.folder_name}</span>
				</Breadcrumb.Link>
			</Breadcrumb.Item>
		{/each}
	</Breadcrumb.List>
</Breadcrumb.Root>
