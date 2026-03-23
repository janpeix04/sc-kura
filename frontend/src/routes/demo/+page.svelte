<script lang="ts">
	import { m } from "$lib/paraglide/messages";
	import { localizeHref } from "$lib/paraglide/runtime";
</script>

<div>
    <h1>{m.welcome()}</h1>

    <a href={localizeHref("/")}>home page</a>
</div>