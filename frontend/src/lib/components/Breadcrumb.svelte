<script lang="ts">
	import type { Breadcrumbs } from '$lib/client';
    import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';

    let {
        breadcrumbs
    }: {
        breadcrumbs: Breadcrumbs[]
    } = $props();
</script>
<Breadcrumb.Root>
	<Breadcrumb.List class="text-lg">
		<Breadcrumb.Item>
			<Breadcrumb.Link href={localizeHref('/my-files')}>
				<span class="text-2xl">{m.my_files()}</span>
			</Breadcrumb.Link>
		</Breadcrumb.Item>
		{#each breadcrumbs as breadcrumb}
			<Breadcrumb.Separator class="flex" />
			<Breadcrumb.Item>
				<Breadcrumb.Link href={localizeHref(`/folder/${breadcrumb.folder_id}`)}>
					<span class="text-2xl">{breadcrumb.folder_name}</span>
				</Breadcrumb.Link>
			</Breadcrumb.Item>
		{/each}
	</Breadcrumb.List>
</Breadcrumb.Root>
