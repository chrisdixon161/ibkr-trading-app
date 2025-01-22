<script setup>
import { ref } from "vue";
import { supabase } from "../supabase";

const email = ref("");
const password = ref("");
const error = ref(null);

const login = async () => {
	const { user, error: loginError } = await supabase.auth.signInWithPassword({
		email: email.value,
		password: password.value,
	});

	if (loginError) {
		error.value = loginError.message;
	} else {
		console.log("Logged in as:", user.email);
	}
};
</script>

<template>
	<div>
		<form @submit.prevent="login">
			<input v-model="email" type="email" placeholder="Email" required />
			<input
				v-model="password"
				type="password"
				placeholder="Password"
				required
			/>
			<button type="submit">Login</button>
		</form>
		<p v-if="error">{{ error }}</p>
	</div>
</template>
