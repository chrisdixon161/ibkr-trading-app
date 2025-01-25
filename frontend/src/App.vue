<template>
	<div>
		<header>
			<div class="wrapper">
				<p>error: {{ error || "none" }}</p>
				<p>Subscribed to plan: {{ isSubscribed }}</p>
				<hr />
				<Dashboard v-if="isSubscribed" :user="user" />
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

const isSubscribed = ref(false);
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

			// Verify user has an active plan
			await axios.get("http://127.0.0.1:8000/api/verify-access", {
				headers: { Authorization: `Bearer ${token}` },
			});

			// If access is verified, set isSubscribed to true
			isSubscribed.value = true;
		} else {
			isSubscribed.value = false;
		}
	} catch (err) {
		console.error("Access verification failed:", err.response?.data || err);
		localStorage.removeItem("authToken"); // Remove token if verification fails
		isSubscribed.value = false; // Set isSubscribed to false on error
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
