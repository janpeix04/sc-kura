<script lang="ts">
    import * as Form from "$lib/components/ui/form/index";
    import { Label } from "$lib/components/ui/label/index";
    import { Input } from "$lib/components/ui/input/index";
    import {
        type SuperValidated,
        type Infer,
        superForm
    } from 'sveltekit-superforms';
    import { zod4Client } from "sveltekit-superforms/adapters";
	import { signupSchema, type SignupSchema } from "$lib/schemas/auth";

    let { data }: { data : { form: SuperValidated<Infer<SignupSchema>>}} = $props();

    const form = superForm(data.form, {
        validators: zod4Client(signupSchema)
    });

    const { form: formData, enhance } = form;
</script>

<form method='POST' use:enhance>
    <Form.Field {form} name='username'>
        <Form.Control>
            {#snippet children({ props })}
                <Form.Label>Username</Form.Label>
                <Input 
                    {...props}
                    bind:value={$formData.username}
                    type='text'
                    autocomplete='username'
                    required
                />
            {/snippet}
        </Form.Control>
        <Form.FieldErrors />
    </Form.Field>

    <Form.Field {form} name='email'>
        <Form.Control>
            {#snippet children({ props })}
                <Form.Label>Email</Form.Label>
                <Input 
                    {...props}
                    bind:value={$formData.email}
                    type='email'
                    autocomplete='email'
                    required
                />
            {/snippet}
        </Form.Control>
        <Form.FieldErrors />
    </Form.Field>

    <Form.Field {form} name='password'>
        <Form.Control>
            {#snippet children({ props })}
                <Form.Label>Password</Form.Label>
                <Input 
                    {...props}
                    bind:value={$formData.password}
                    type='password'
                    autocomplete='new-password'
                    required
                />
            {/snippet}
        </Form.Control>
        <Form.FieldErrors />
    </Form.Field>

    <Form.Field {form} name='confirm-password'>
        <Form.Control>
            {#snippet children({ props })}
                <Form.Label>Confirm Password</Form.Label>
                <Input 
                    {...props}
                    bind:value={$formData['confirm-password']}
                    type='password'
                    autocomplete='current-password'
                    required
                />
            {/snippet}
        </Form.Control>
        <Form.FieldErrors />
    </Form.Field>
    <Form.Button>Sign up</Form.Button>
</form>