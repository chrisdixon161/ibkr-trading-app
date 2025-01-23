<template>
	<div>
		<h1>Login</h1>
		<form @submit.prevent="login">
			<div>
				<label>Email:</label>
				<input v-model="email" type="email" required />
			</div>
			<div>
				<label>Password:</label>
				<input v-model="password" type="password" required />
			</div>
			<button type="submit">Login</button>
		</form>
		<p v-if="error" style="color: red">{{ error }}</p>
	</div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

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
		// Log and display the error
		console.error("Login error:", err.response?.data || err);
		error.value =
			err.response?.data?.detail || "An error occurred during login.";
	}
};
</script>
