<script lang="ts">
    let { data } = $props();
</script>

<div>
    {#if data.success}
        <p>{data.success}</p>
    {:else}
        <p>{data.error}</p>
    {/if}
</div>