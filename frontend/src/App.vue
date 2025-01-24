<template>
	<div>
		<header>
			<div class="wrapper">
				<p>error: {{ error || "none" }}</p>
				<p>authenticated: {{ isAuthenticated }}</p>
				<hr />
				<Dashboard v-if="isAuthenticated" :user="user" />
				<Login v-else />
			</div>
		</header>
	</div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import axios from "axios";
import Dashboard from "./components/Dashboard.vue";
import Login from "./components/Login.vue";

const isAuthenticated = ref(false);
const user = ref(null);
const error = ref(null);

// Check authentication status and validate access
onMounted(async () => {
	try {
		const token = localStorage.getItem("authToken");
		if (token) {
			// Decode and set user details
			const decodedToken = decodeToken(token);
			user.value = decodedToken;

			// Verify user access
			await axios.get("http://127.0.0.1:8000/api/verify-access", {
				headers: { Authorization: `Bearer ${token}` },
			});

			// If access is verified, set isAuthenticated to true
			isAuthenticated.value = true;
		} else {
			isAuthenticated.value = false;
		}
	} catch (err) {
		console.error("Access verification failed:", err.response?.data || err);
		localStorage.removeItem("authToken"); // Remove token if verification fails
		isAuthenticated.value = false; // Set isAuthenticated to false on error
		error.value =
			err.response?.data?.detail || "Access denied or session expired.";
	}
});

// Function to decode the JWT token
const decodeToken = (token) => {
	try {
		const payload = JSON.parse(atob(token.split(".")[1]));
		return { id: payload.sub, email: payload.email };
	} catch (error) {
		console.error("Invalid token:", error);
		return null;
	}
};
</script>

<style scoped>
.wrapper {
	display: flex;
	justify-content: center;
	align-items: center;
	flex-direction: column;
	height: 100vh;
}
</style>
