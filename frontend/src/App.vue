<script setup>
import { onMounted, ref } from "vue";
import Dashboard from "./components/Dashboard.vue";
import Login from "./components/Login.vue";
</script>

<template>
	<div>
		<header>
			<div class="wrapper">
				<Dashboard />
				<Login />
			</div>
		</header>
	</div>
</template>

<style scoped></style>
