<script lang="ts">
    import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import { House } from '@lucide/svelte';

    let { 
        segments,
        url
    }: {
        segments: string[];
        url: string;
    } = $props();
</script>

<Breadcrumb.Root>
	<Breadcrumb.List class="mb-2 px-2">
		<Breadcrumb.Item>
			<Breadcrumb.Link href={url}><House class="size-5" /></Breadcrumb.Link>
		</Breadcrumb.Item>
		{#each segments as folder, idx (idx)}
			<Breadcrumb.Separator />
			<Breadcrumb.Item>
				<Breadcrumb.Link href={`${url}/${segments.slice(0, idx + 1).join('/')}`}>
					{folder}
				</Breadcrumb.Link>
			</Breadcrumb.Item>
		{/each}
	</Breadcrumb.List>
</Breadcrumb.Root>
