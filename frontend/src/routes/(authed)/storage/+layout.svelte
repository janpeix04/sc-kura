<script lang="ts">
	import type { AvailableSpace } from "$lib/client";
	import AppSidebar from "$lib/components/AppSidebar.svelte";
    import * as Sidebar from '$lib/components/ui/sidebar/index.js';

    let { data, children } = $props();
</script>

<AppSidebar user={data.user} availableSpace={data.availableSpace as AvailableSpace} />
<Sidebar.Inset class="flex flex-1 flex-col overflow-hidden">
    {@render children()}
</Sidebar.Inset>