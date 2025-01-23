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

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
const email = ref("");
const password = ref("");
const error = ref(null);
const router = useRouter();

const login = async () => {
	try {
		const response = await axios.post("http://127.0.0.1:8000/api/login", {
			email: email.value,
			password: password.value,
		});
		const { access_token } = response.data;
		localStorage.setItem("authToken", access_token);
		router.push("/dashboard");
	} catch (err) {
		error.value = err.response?.data?.detail || "An error occurred";
	}
};
</script>
